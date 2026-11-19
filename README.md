# Champions of ZED — русская веб-книга

Весь исходный текст находится в **[CoZ_книга.md](CoZ_книга.md)**. Не нужно вручную редактировать сгенерированные главы — конвертер создаёт их автоматически.

## Локальная сборка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/convert.py
python -m unittest discover -s tests -v
mkdocs serve
```

Сайт будет доступен по адресу http://127.0.0.1:8000/. Для сборки статического HTML выполните `mkdocs build --strict`.

## GitHub Pages

Откройте **Settings → Pages → Build and deployment → Source → GitHub Actions**. После слияния pull request в `main` сайт автоматически опубликуется на https://dexius9669.github.io/zero_edition/.

## Как устроена книга

- `#` — главы, части и приложения. Навигация генерируется из этих заголовков.
- `##` и `###` — подзаголовки внутри главы.
- Все 172 таблицы остаются в Markdown; широкие прокручиваются по горизонтали.
- Контейнеры `.note`, `.statblock`, `.center`, `.coz-title` становятся стилизованными HTML-блоками.
- Комментарии с номерами страниц оригинала скрыты в веб-версии.
- Тёмная тема включается по системным настройкам, доступен переключатель на светлую.
- Публикация через GitHub Actions, с проверкой сборки на pull requests.

Исходный русский перевод не редактируется конвертером.
