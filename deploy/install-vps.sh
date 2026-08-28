#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer as root: sudo bash deploy/install-vps.sh"
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
SERVICE_NAME="zefronmusic"
SERVICE_USER="zefronmusic"
VENV_DIR="${APP_DIR}/.venv"

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This installer supports Debian/Ubuntu VPS systems with apt-get."
  exit 1
fi

echo "Installing system dependencies..."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ffmpeg \
  git \
  python3 \
  python3-pip \
  python3-venv

if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
  useradd --system --home-dir "${APP_DIR}" --shell /usr/sbin/nologin "${SERVICE_USER}"
fi

echo "Creating Python virtual environment..."
python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/pip" install --requirement "${APP_DIR}/requirements.txt"

chown -R "${SERVICE_USER}:${SERVICE_USER}" "${APP_DIR}"
chmod 600 "${APP_DIR}/.env" 2>/dev/null || true

install -m 0644 "${APP_DIR}/deploy/zefronmusic.service" \
  "/etc/systemd/system/${SERVICE_NAME}.service"
sed -i "s|APP_DIR|${APP_DIR}|g" \
  "/etc/systemd/system/${SERVICE_NAME}.service"

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}.service"

if [[ ! -f "${APP_DIR}/.env" ]]; then
  cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
  chown "${SERVICE_USER}:${SERVICE_USER}" "${APP_DIR}/.env"
  chmod 600 "${APP_DIR}/.env"
  echo
  echo "Created ${APP_DIR}/.env from .env.example."
  echo "Fill in the Telegram, MongoDB, and session values, then run:"
  echo "  sudo systemctl start ${SERVICE_NAME}"
  exit 0
fi

systemctl restart "${SERVICE_NAME}.service"
systemctl --no-pager --full status "${SERVICE_NAME}.service"