"""Dựng cụm PostgreSQL local tách biệt, chỉ dành cho dữ liệu thử."""

import asyncio
import os
import secrets
import subprocess
import sys
from pathlib import Path

import asyncpg
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / ".local"
DATA = LOCAL / "postgres"
BIN = Path("C:/Program Files/PostgreSQL/18/bin")
PORT = 5543


def update_environment(values: dict[str, str]) -> None:
    path = ROOT / ".env"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    existing = {line.split("=", 1)[0] for line in lines if "=" in line}
    result = [
        f"{line.split('=', 1)[0]}={values[line.split('=', 1)[0]]}"
        if line.split("=", 1)[0] in values
        else line
        for line in lines
    ]
    result.extend(f"{key}={value}" for key, value in values.items() if key not in existing)
    path.write_text("\n".join(result) + "\n", encoding="utf-8")


async def provision() -> None:
    LOCAL.mkdir(exist_ok=True)
    admin_file = LOCAL / "admin.env"
    saved = dotenv_values(admin_file)
    admin_password = saved.get("PGPASSWORD") or secrets.token_urlsafe(36)
    app_password = secrets.token_urlsafe(36)
    if DATA.exists() and not saved:
        if "--recover-initialization" not in sys.argv:
            raise RuntimeError("Cụm đã tồn tại; cần phục hồi lần khởi tạo bị gián đoạn.")
        hba = DATA / "pg_hba.conf"
        original = hba.read_text(encoding="utf-8")
        try:
            hba.write_text(
                "host all tax_clear_admin 127.0.0.1/32 trust\n" + original, encoding="utf-8"
            )
            await asyncio.to_thread(
                subprocess.run, [str(BIN / "pg_ctl.exe"), "-D", str(DATA), "reload"], check=True
            )
            recovery = await asyncpg.connect(
                host="127.0.0.1", port=PORT, user="tax_clear_admin", database="postgres"
            )
            try:
                sql = await recovery.fetchval(
                    "SELECT format('ALTER ROLE tax_clear_admin PASSWORD %L', $1::text)",
                    admin_password,
                )
                await recovery.execute(sql)
            finally:
                await recovery.close()
        finally:
            hba.write_text(original, encoding="utf-8")
            await asyncio.to_thread(
                subprocess.run, [str(BIN / "pg_ctl.exe"), "-D", str(DATA), "reload"], check=True
            )
    admin_file.write_text(
        f"PGUSER=tax_clear_admin\nPGPASSWORD={admin_password}\nPGPORT={PORT}\n",
        encoding="utf-8",
    )
    password_file = LOCAL / "init-password"
    if not DATA.exists():
        password_file.write_text(admin_password, encoding="utf-8")
        try:
            await asyncio.to_thread(
                subprocess.run,
                [
                    str(BIN / "initdb.exe"),
                    "-D",
                    str(DATA),
                    "-U",
                    "tax_clear_admin",
                    "--auth=scram-sha-256",
                    "--encoding=UTF8",
                    "--locale=C",
                    f"--pwfile={password_file}",
                ],
                check=True,
                capture_output=True,
            )
        finally:
            password_file.unlink(missing_ok=True)
    state = await asyncio.to_thread(
        subprocess.run, [str(BIN / "pg_ctl.exe"), "-D", str(DATA), "status"], capture_output=True
    )
    if state.returncode != 0:
        await asyncio.to_thread(
            subprocess.run,
            [
                str(BIN / "pg_ctl.exe"),
                "-D",
                str(DATA),
                "-l",
                str(LOCAL / "postgres.log"),
                "-o",
                f"-p {PORT} -h 127.0.0.1",
                "-w",
                "start",
            ],
            check=True,
            capture_output=True,
        )
    connection = await asyncpg.connect(
        host="127.0.0.1",
        port=PORT,
        user="tax_clear_admin",
        password=admin_password,
        database="postgres",
    )
    try:
        if await connection.fetchval("SELECT 1 FROM pg_roles WHERE rolname='tax_clear_app'"):
            raise RuntimeError("Vai trò đã tồn tại; không đổi mật khẩu hoặc ghi đè DB.")
        role_sql = await connection.fetchval(
            "SELECT format('CREATE ROLE tax_clear_app LOGIN NOSUPERUSER NOCREATEDB "
            "NOCREATEROLE PASSWORD %L', $1::text)",
            app_password,
        )
        await connection.execute(role_sql)
        await connection.execute("CREATE DATABASE tax_clear_ai_dev OWNER tax_clear_app")
        await connection.execute("CREATE DATABASE tax_clear_ai_test OWNER tax_clear_app")
        await connection.execute("REVOKE CONNECT ON DATABASE tax_clear_ai_dev FROM PUBLIC")
        await connection.execute("REVOKE CONNECT ON DATABASE tax_clear_ai_test FROM PUBLIC")
    finally:
        await connection.close()
    url = f"postgresql+asyncpg://tax_clear_app:{app_password}@127.0.0.1:{PORT}/"
    update_environment(
        {
            "DATABASE_URL": url + "tax_clear_ai_dev",
            "TEST_DATABASE_URL": url + "tax_clear_ai_test",
            "JWT_SECRET_KEY": secrets.token_urlsafe(48),
            "BOOTSTRAP_USERNAME": "demo",
            "BOOTSTRAP_PASSWORD": secrets.token_urlsafe(18),
            "FRONTEND_ORIGIN": "http://localhost:3000",
        }
    )
    print("DB_READY: tax_clear_ai_dev + tax_clear_ai_test, loopback:5543; secrets in .env only")


if __name__ == "__main__":
    os.chdir(ROOT)
    asyncio.run(provision())
