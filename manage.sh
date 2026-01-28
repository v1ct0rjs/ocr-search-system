#!/bin/bash

set -e

PROJECT_NAME="OCR SEARCH SYSTEM"
INDEX_NAME="documents"

function header() {
  echo ""
  echo "=============================="
  echo "  $PROJECT_NAME"
  echo "=============================="
}

function up() {
  header
  echo "Levantando servicios..."
  docker compose up -d
  echo "Sistema iniciado"
}

function down() {
  header
  echo "Parando servicios..."
  docker compose down
  echo "Sistema detenido"
}

function restart() {
  header
  echo "Reiniciando servicios..."
  docker compose restart
  echo "Reinicio completo"
}

function rebuild() {
  header
  echo "Rebuild completo (sin cache)..."
  docker compose build --no-cache
  docker compose up -d
  echo "Rebuild terminado"
}

function logs_api() {
  docker compose logs -f api_service
}

function logs_ocr() {
  docker compose logs -f ocr_service
}

function logs_es() {
  docker compose logs -f elasticsearch
}

function status() {
  header
  docker compose ps
}

function reset_index() {
  header
  echo "orrando índice Elasticsearch..."
  curl -s -X DELETE "http://localhost:9200/$INDEX_NAME" || true
  echo ""
  echo "Reiniciando OCR para reindexar todo..."
  docker compose restart ocr_service
  echo "Reindexación en marcha (mira logs_ocr)"
}

function search_test() {
  header
  echo "🔍 Prueba de búsqueda:"
  read -p "Texto a buscar: " query
  curl "http://localhost:8000/search?q=$query"
  echo ""
}

function help_menu() {
  header
  echo "Uso: ./manage.sh [comando]"
  echo ""
  echo "Comandos disponibles:"
  echo "  up            → Iniciar todo el sistema"
  echo "  down          → Parar todo"
  echo "  restart       → Reiniciar servicios"
  echo "  rebuild       → Rebuild completo sin cache"
  echo "  status        → Ver estado contenedores"
  echo ""
  echo "  logs-api      → Logs API"
  echo "  logs-ocr      → Logs OCR"
  echo "  logs-es       → Logs Elasticsearch"
  echo ""
  echo "  reset-index   → Borra índice y reindexa documentos"
  echo "  search        → Probar búsqueda desde terminal"
  echo ""
}

case "$1" in
  up) up ;;
  down) down ;;
  restart) restart ;;
  rebuild) rebuild ;;
  status) status ;;
  logs-api) logs_api ;;
  logs-ocr) logs_ocr ;;
  logs-es) logs_es ;;
  reset-index) reset_index ;;
  search) search_test ;;
  *) help_menu ;;
esac