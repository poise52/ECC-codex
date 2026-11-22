# Плагины из текущего набора Codex

Снимок от 22 ноября 2026 года: 21 запись. Это отдельный каталог от 20 собственных
ECC-скиллов. Основная установка ECC не включает сторонние плагины автоматически.

## Установка

Команды из корня ECC:

```sh
./install.sh --list-plugins
./install.sh --plugins cc-skills --dry-run
./install.sh --plugins cc-skills
./install.sh --plugins github gmail google-calendar google-drive
./install.sh --plugins all --dry-run
```

Для установки нужен Codex CLI с командами `codex plugin add` и
`codex plugin marketplace add` (проверено по интерфейсу 0.171.0-alpha.13).
`--list-plugins` и `--dry-run` работают без Codex и сети.

`--plugins all` устанавливает `cc-skills` и четыре официальных marketplace-пакета;
для остальных записей выводит способ подключения. На другой машине сервисы
могут попросить вход в аккаунт и подтверждение доступа. Завершай такой вход
в штатном интерфейсе Codex/ChatGPT.

Для `cc-skills` установщик регистрирует marketplace `ecc-plugins` из текущего
checkout, затем вызывает `codex plugin add cc-skills@ecc-plugins`. Подключённый
marketplace с тем же именем, но другим путём вызывает ошибку до установки.
Уже установленные пакеты пропускаются, их флаги enabled/disabled сохраняются.
При ошибке предыдущие успешные установки остаются на месте; автоматического
удаления плагинов или подключений нет.

Plugin-режим относится к пользовательскому native plugin manager и не принимает
`--project`, `--dest`, `--profile` или `--uninstall`. Последние параметры относятся
к установке ECC-скиллов. Для удаления плагина используй штатный интерфейс Plugins.

## Что находится прямо в репозитории

[cc-skills](cc-skills/UPSTREAM.json): 21 скилл из установленной версии
[samber/cc-skills](https://github.com/samber/cc-skills), MIT, commit
`123cb155f5ab5751fc13c8027fbfa5eb0d3773c6`. Включены engineering/design,
исследование, тексты и маркетинг. Лицензия лежит рядом с пакетом.

Снимок сохраняет исходные инструкции и ресурсы; он не является переработанным
языковым профилем ECC. Если `cc-skills` уже подключён через `~/.agents/skills`,
выбери один способ подключения, чтобы не показывать одни скиллы дважды.

Официальные плагины и runtime Codex не копируются из локального кэша. Их
сервисы, доступность и авторизация зависят от приложения и аккаунта; копия
файлов не переносит серверные инструменты.

## Каталог

| Пакет | Название | Способ получения | Основание снимка |
| --- | --- | --- | --- |
| `browser` | Browser | Runtime/встроенная функция приложения | `installed-cli` |
| `cc-skills` | Engineering & Marketing Skills (21 skills) | Включён в ECC | `installed-global-skills` |
| `codex-app-tools` | codex-app-tools | Runtime/встроенная функция приложения | `installed-cli` |
| `computer-use` | Computer Use | Runtime/встроенная функция приложения | `installed-cli` |
| `documents` | Documents | Runtime/встроенная функция приложения | `installed-cli` |
| `github` | GitHub | Официальный marketplace Codex | `installed-connector` |
| `gmail` | Gmail | Официальный marketplace Codex | `installed-connector` |
| `google-calendar` | Google Calendar | Официальный marketplace Codex | `installed-connector` |
| `google-contacts` | Google Contacts | Plugins в приложении, подключение аккаунта | `installed-connector` |
| `google-drive` | Google Drive | Официальный marketplace Codex | `installed-connector` |
| `openai-templates` | Default templates | Runtime/встроенная функция приложения | `cached-bundle` |
| `pages` | Pages | Runtime/встроенная функция приложения | `cached-bundle` |
| `pdf` | PDF | Runtime/встроенная функция приложения | `installed-cli` |
| `plugin-management` | Plugin Management | Runtime/встроенная функция приложения | `cached-bundle` |
| `presentations` | Presentations | Runtime/встроенная функция приложения | `installed-cli` |
| `sites` | Sites | Plugins в приложении, подключение аккаунта | `installed-connector` |
| `spreadsheets` | Spreadsheets | Runtime/встроенная функция приложения | `installed-cli` |
| `template-creator` | Template Creator | Runtime/встроенная функция приложения | `installed-cli` |
| `unified-computer-use` | unified-computer-use | Runtime/встроенная функция приложения | `installed-cli` |
| `visualize` | Visualize | Runtime/встроенная функция приложения | `installed-cli` |
| `work-pets` | Pets | Runtime/встроенная функция приложения | `cached-bundle` |

`installed-cli` — native CLI подтвердил установку; `installed-connector` —
Plugin Management подтвердил установку плагина в приложении; `installed-global-skills` —
найден пользовательский набор скиллов. `cached-bundle` означает только наличие
пакета в runtime-кэше, без отдельного подтверждения текущей установки.

Для Google Contacts и Sites открой [Plugins](https://chatgpt.com/plugins) в
поддерживаемом приложении и выбери нужное подключение. Для host-записей нужен
Codex/ChatGPT с соответствующим runtime и доступной функцией. Каталог отражает
снимок окружения, а не гарантирует доступность всех функций на любом клиенте.

Формат native marketplace и команды сверены с
[документацией OpenAI](https://developers.openai.com/plugins/build/plugins).
Происхождение и границы проверки указаны в [SOURCES.md](../SOURCES.md).
