from __future__ import annotations

import argparse
from getpass import getpass
from typing import List, Optional, Sequence, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .exceptions import (
    EntryNotFound,
    InvalidMasterPassword,
    VaultAlreadyExists,
    VaultIntegrityError,
    VaultNotInitialized,
    VaultError,
)
from .models import Vault, VaultEntry
from .passwords import GeneratorOptions, SYMBOL_SETS, generate_password
from .storage import DEFAULT_VAULT_PATH, SecureVault, VaultStorage
from .api.storage import APIVaultStorage, SecureVaultAPI
from .api.client import APIClient, setup_api_connection, DEFAULT_CONFIG_PATH

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pass-manager",
        description="AES-GCM ile şifrelenmiş kişiye özel şifre kasası.",
    )
    parser.add_argument(
        "--vault",
        dest="vault_path",
        default=str(DEFAULT_VAULT_PATH),
        help=f"Kasa dosyasının yolu (varsayılan: {DEFAULT_VAULT_PATH}).",
    )
    parser.add_argument(
        "--api",
        dest="use_api",
        action="store_true",
        help="API sunucusunu kullan (yerel dosya yerine).",
    )
    parser.add_argument(
        "--api-url",
        dest="api_url",
        default="http://localhost:8000",
        help="API sunucu URL'i (varsayılan: http://localhost:8000).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Yeni bir şifre kasası oluştur.")
    
    api_setup_parser = subparsers.add_parser("api-setup", help="API bağlantısını kur.")
    api_setup_parser.add_argument(
        "--api-url",
        dest="api_url",
        default="http://localhost:8000",
        help="API sunucu URL'i.",
    )

    add_parser = subparsers.add_parser("add", help="Kasa içine yeni kayıt ekle.")
    add_parser.add_argument("--service", required=True, help="Servis adı (ör. github).")
    add_parser.add_argument("--username", required=True, help="Servis kullanıcı adı.")
    add_parser.add_argument("--password", help="Parola değeri. Boşsa CLI sorar.")
    add_parser.add_argument("--notes", default="", help="İsteğe bağlı not.")
    add_parser.add_argument("--tags", help="Virgülle ayrılmış etiket listesi.")
    add_parser.add_argument(
        "--auto",
        action="store_true",
        help="Parola otomatik üretilecek.",
    )
    add_parser.add_argument(
        "--length",
        type=int,
        default=24,
        help="Otomatik parola uzunluğu (varsayılan 24).",
    )
    add_parser.add_argument(
        "--symbols",
        choices=list(SYMBOL_SETS.keys()),
        default="soft",
        help="Otomatik parola sembol modu.",
    )
    add_parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="Benzemeyen karakterleri filtreleme.",
    )

    list_parser = subparsers.add_parser("list", help="Kayıtları tablo halinde göster.")
    list_parser.add_argument("--filter", help="Servis, kullanıcı veya etikette arama.")

    show_parser = subparsers.add_parser("show", help="Belirli bir kaydı görüntüle.")
    show_parser.add_argument("--id", required=True, help="Kayıt ID değeri.")
    show_parser.add_argument(
        "--reveal",
        action="store_true",
        help="Parolayı düz metin olarak göster.",
    )

    delete_parser = subparsers.add_parser("delete", help="Kaydı kalıcı olarak sil.")
    delete_parser.add_argument("--id", required=True, help="Silinecek kayıt ID'si.")

    gen_parser = subparsers.add_parser("generate", help="Bağımsız parola üret.")
    gen_parser.add_argument("--length", type=int, default=28)
    gen_parser.add_argument(
        "--symbols",
        choices=list(SYMBOL_SETS.keys()),
        default="hard",
        help="Sembol yoğunluğu.",
    )
    gen_parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="Benzemeyen karakterleri filtreleme.",
    )
    gen_parser.add_argument(
        "--no-require-each",
        action="store_true",
        help="Her karakter grubundan en az bir tane kullanma zorunluluğunu kaldır.",
    )

    return parser


def prompt_master_password(confirm: bool = False) -> str:
    while True:
        password = getpass("Ana parola: ").strip()
        if len(password) < 8:
            console.print("[red]Ana parola en az 8 karakter olmalıdır.[/red]")
            continue
        if not confirm:
            return password
        password_confirm = getpass("Ana parola (tekrar): ").strip()
        if password != password_confirm:
            console.print("[red]Parolalar eşleşmedi. Tekrar deneyin.[/red]")
            continue
        return password


def prompt_entry_password() -> str:
    while True:
        password = getpass("Kayıt parolası: ").strip()
        if len(password) < 6:
            console.print("[red]Parola en az 6 karakter olmalı.[/red]")
            continue
        confirmation = getpass("Kayıt parolası (tekrar): ").strip()
        if password != confirmation:
            console.print("[red]Parolalar eşleşmedi.[/red]")
            continue
        return password


def parse_tags(text: Optional[str]) -> List[str]:
    if not text:
        return []
    return [tag.strip() for tag in text.split(",") if tag.strip()]


def load_vault_from_args(args) -> Tuple[SecureVault, str, Vault]:
    if args.use_api:
        try:
            client = APIClient.load_config()
        except FileNotFoundError:
            console.print("[red]API konfigürasyonu bulunamadı. Önce 'api-setup' komutunu çalıştırın.[/red]")
            raise
        api_storage = APIVaultStorage(client.api_url, client.token)
        secure_vault = SecureVaultAPI(api_storage)
    else:
        storage = VaultStorage(args.vault_path)
        secure_vault = SecureVault(storage)
    master = prompt_master_password()
    vault = secure_vault.load_vault(master)
    return secure_vault, master, vault


def handle_init(args) -> None:
    if args.use_api:
        try:
            client = APIClient.load_config()
        except FileNotFoundError:
            console.print("[red]API konfigürasyonu bulunamadı. Önce 'api-setup' komutunu çalıştırın.[/red]")
            return
        api_storage = APIVaultStorage(client.api_url, client.token)
        secure_vault = SecureVaultAPI(api_storage)
        location_info = f"API: {client.api_url}"
    else:
        storage = VaultStorage(args.vault_path)
        secure_vault = SecureVault(storage)
        location_info = f"Konum: [bold]{storage.path}[/bold]"
    
    master_password = prompt_master_password(confirm=True)
    try:
        secure_vault.init_vault(master_password)
    except VaultAlreadyExists:
        console.print("[red]Bu konumda zaten bir kasa bulunuyor.[/red]")
        return
    console.print(
        Panel.fit(
            f"Kasa oluşturuldu!\n{location_info}",
            title="Başarılı",
            border_style="green",
        )
    )


def handle_add(args) -> None:
    secure_vault, master, vault = load_vault_from_args(args)
    if args.auto:
        options = GeneratorOptions(
            length=args.length,
            symbols=args.symbols,
            allow_ambiguous=args.allow_ambiguous,
        )
        password = generate_password(options)
        generated = True
    elif args.password:
        password = args.password
        generated = False
    else:
        password = prompt_entry_password()
        generated = False

    entry = VaultEntry(
        service=args.service,
        username=args.username,
        password=password,
        notes=args.notes,
        tags=parse_tags(args.tags),
    )
    vault.add_entry(entry)
    secure_vault.save_vault(master, vault)
    console.print(
        Panel.fit(
            f"Kayıt ID: [bold]{entry.entry_id}[/bold]\nServis: {entry.service}\nKullanıcı: {entry.username}",
            title="Kayıt eklendi",
            border_style="green",
        )
    )
    if generated:
        console.print(
            Panel(
                f"[bold yellow]{password}[/bold yellow]",
                title="Otomatik Üretilen Parola",
                subtitle="Kopyalayıp güvenli şekilde saklayın",
                border_style="yellow",
            )
        )


def handle_list(args) -> None:
    _, _, vault = load_vault_from_args(args)
    entries = vault.list_entries(keyword=args.filter)
    if not entries:
        console.print("[yellow]Hiç kayıt bulunamadı.[/yellow]")
        return

    table = Table(title=f"{len(entries)} kayıt bulundu", show_lines=False)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Servis", style="white")
    table.add_column("Kullanıcı", style="magenta")
    table.add_column("Etiketler", style="green")
    table.add_column("Güncellendi", style="yellow")

    for entry in entries:
        tags = ", ".join(entry.tags) if entry.tags else "-"
        table.add_row(
            entry.entry_id,
            entry.service,
            entry.username,
            tags,
            entry.updated_at,
        )
    console.print(table)


def handle_show(args) -> None:
    _, _, vault = load_vault_from_args(args)
    try:
        entry = vault.get_entry(args.id)
    except EntryNotFound as exc:
        console.print(f"[red]{exc}[/red]")
        return

    password_display = entry.password if args.reveal else "●" * 12
    body = (
        f"Servis : [bold]{entry.service}[/bold]\n"
        f"Kullanıcı : {entry.username}\n"
        f"Parola : {password_display}\n"
        f"Etiketler : {', '.join(entry.tags) if entry.tags else '-'}\n"
        f"Notlar : {entry.notes or '-'}\n"
        f"Oluşturuldu : {entry.created_at}\n"
        f"Güncellendi : {entry.updated_at}"
    )
    console.print(
        Panel(body, title=f"Kayıt Detayı ({entry.entry_id})", border_style="blue")
    )


def handle_delete(args) -> None:
    secure_vault, master, vault = load_vault_from_args(args)
    try:
        entry = vault.delete_entry(args.id)
    except EntryNotFound as exc:
        console.print(f"[red]{exc}[/red]")
        return
    secure_vault.save_vault(master, vault)
    console.print(
        Panel.fit(
            f"{entry.service} / {entry.username}",
            title="Kayıt silindi",
            border_style="red",
        )
    )


def handle_generate(args) -> None:
    options = GeneratorOptions(
        length=args.length,
        symbols=args.symbols,
        allow_ambiguous=args.allow_ambiguous,
        require_each_category=not args.no_require_each,
    )
    password = generate_password(options)
    console.print(
        Panel(
            f"[bold green]{password}[/bold green]",
            title="Yeni Parola",
            subtitle="Kopyalayıp güvenle saklayın",
        )
    )


def handle_api_setup(args) -> None:
    """API bağlantısını kur."""
    try:
        client = setup_api_connection(args.api_url)
        console.print(
            Panel.fit(
                f"API bağlantısı kuruldu!\nURL: {client.api_url}\nKonfigürasyon: {DEFAULT_CONFIG_PATH}",
                title="Başarılı",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[red]API kurulumu başarısız: {e}[/red]")


def dispatch(args) -> None:
    command_map = {
        "init": handle_init,
        "add": handle_add,
        "list": handle_list,
        "show": handle_show,
        "delete": handle_delete,
        "generate": handle_generate,
        "api-setup": handle_api_setup,
    }
    handler = command_map.get(args.command)
    if not handler:
        raise ValueError(f"Bilinmeyen komut: {args.command}")
    handler(args)


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        dispatch(args)
    except VaultNotInitialized:
        console.print("[red]Önce `init` komutuyla kasa oluşturmalısınız.[/red]")
    except InvalidMasterPassword:
        console.print("[red]Ana parola hatalı veya veri bozuk.[/red]")
    except VaultIntegrityError as exc:
        console.print(f"[red]Kasa bütünlüğü doğrulanamadı: {exc}[/red]")
    except VaultError as exc:
        console.print(f"[red]{exc}[/red]")


if __name__ == "__main__":
    main()

