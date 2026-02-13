# msbaek-claude-plugins Marketplace 배포 가이드

이 문서는 `msbaek-claude-plugins` 저장소를 Claude Code Plugin Marketplace로 등록하고, 사용자가 플러그인을 설치하는 전체 과정을 설명합니다.

## 목차

1. [Marketplace 구조 이해](#1-marketplace-구조-이해)
2. [Marketplace 파일 생성](#2-marketplace-파일-생성)
3. [GitHub에 배포](#3-github에-배포)
4. [사용자 설치 방법](#4-사용자-설치-방법)
5. [플러그인 업데이트](#5-플러그인-업데이트)
6. [검증 및 테스트](#6-검증-및-테스트)
7. [팀 배포 설정](#7-팀-배포-설정)
8. [트러블슈팅](#8-트러블슈팅)

---

## 1. Marketplace 구조 이해

Claude Code Plugin Marketplace는 플러그인을 배포하는 카탈로그입니다. 핵심 구성 요소:

```
msbaek-claude-plugins/                  # Marketplace 저장소 루트
├── .claude-plugin/
│   └── marketplace.json                # (필수) Marketplace 카탈로그
├── msbaek-tdd/                         # 플러그인 디렉토리
│   ├── .claude-plugin/
│   │   └── plugin.json                 # 플러그인 매니페스트
│   ├── agents/
│   │   ├── tdd-red.md
│   │   ├── tdd-green.md
│   │   └── tdd-blue.md
│   └── skills/
│       ├── tdd/SKILL.md
│       ├── tdd-plan/SKILL.md
│       └── tdd-rgb/SKILL.md
└── README.md
```

### 핵심 파일

| 파일 | 역할 |
|------|------|
| `.claude-plugin/marketplace.json` | Marketplace 메타데이터 + 플러그인 목록 정의 |
| `msbaek-tdd/.claude-plugin/plugin.json` | 개별 플러그인 메타데이터 |
| `msbaek-tdd/skills/*/SKILL.md` | 사용자가 `/skill-name`으로 호출하는 Skill |
| `msbaek-tdd/agents/*.md` | Skill이 위임하는 전문 Agent |

---

## 2. Marketplace 파일 생성

### 2.1 marketplace.json 작성

저장소 루트에 `.claude-plugin/marketplace.json`을 생성합니다:

```json
{
  "name": "msbaek-claude-plugins",
  "owner": {
    "name": "msbaek",
    "email": "your-email@example.com"
  },
  "metadata": {
    "description": "TDD workflow plugins for Java/Spring Boot development",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "msbaek-tdd",
      "source": "./msbaek-tdd",
      "description": "Java + Spring Boot TDD workflow plugin with RGB cycle orchestration",
      "version": "1.0.0",
      "author": {
        "name": "msbaek"
      },
      "keywords": ["tdd", "java", "spring-boot", "red-green-blue"],
      "category": "development"
    }
  ]
}
```

### 2.2 필수 필드 설명

**Marketplace 레벨:**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | Yes | Marketplace 식별자 (kebab-case). 사용자가 `/plugin install msbaek-tdd@msbaek-claude-plugins` 형태로 사용 |
| `owner.name` | string | Yes | 관리자 이름 |
| `owner.email` | string | No | 관리자 연락처 |
| `metadata.description` | string | No | Marketplace 설명 |
| `metadata.version` | string | No | Marketplace 버전 |
| `plugins` | array | Yes | 플러그인 목록 |

**Plugin 엔트리:**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | Yes | 플러그인 식별자 (kebab-case) |
| `source` | string/object | Yes | 플러그인 소스 경로 또는 Git URL |
| `description` | string | No | 플러그인 설명 |
| `version` | string | No | 플러그인 버전 |
| `category` | string | No | 카테고리 분류 |
| `keywords` | array | No | 검색용 키워드 |

### 2.3 Plugin Source 유형

**상대 경로** (같은 저장소 내 플러그인):
```json
{ "source": "./msbaek-tdd" }
```

**GitHub 저장소** (외부 저장소 참조):
```json
{
  "source": {
    "source": "github",
    "repo": "msbaek/some-other-plugin"
  }
}
```

**Git URL** (GitHub 외 Git 호스팅):
```json
{
  "source": {
    "source": "url",
    "url": "https://gitlab.com/msbaek/plugin.git"
  }
}
```

**버전 고정** (특정 브랜치/태그/커밋):
```json
{
  "source": {
    "source": "github",
    "repo": "msbaek/some-plugin",
    "ref": "v1.0.0",
    "sha": "a1b2c3d4e5f6..."
  }
}
```

---

## 3. GitHub에 배포

### 3.1 저장소 생성 및 Push

```bash
cd ~/git/msbaek-claude-plugins

# GitHub 저장소 생성 (gh CLI 사용)
gh repo create msbaek-claude-plugins --public --description "Claude Code TDD Plugin Marketplace"

# 또는 private으로 생성
gh repo create msbaek-claude-plugins --private --description "Claude Code TDD Plugin Marketplace"

# Push
git remote add origin git@github.com:msbaek/msbaek-claude-plugins.git
git push -u origin main
```

### 3.2 배포 전 체크리스트

- [ ] `.claude-plugin/marketplace.json` 파일이 저장소 루트에 존재
- [ ] marketplace.json의 JSON 문법이 유효
- [ ] 각 플러그인 디렉토리에 `.claude-plugin/plugin.json` 존재
- [ ] 모든 `source` 경로가 올바른 디렉토리를 가리킴
- [ ] README.md에 설치 방법 문서화

---

## 4. 사용자 설치 방법

### 4.1 Marketplace 추가

사용자는 먼저 Marketplace를 등록합니다:

```
# GitHub 저장소에서 추가 (권장)
/plugin marketplace add msbaek/msbaek-claude-plugins

# 또는 전체 URL로 추가
/plugin marketplace add https://github.com/msbaek/msbaek-claude-plugins.git

# 로컬 경로로 추가 (개발/테스트용)
/plugin marketplace add ./path/to/msbaek-claude-plugins
```

### 4.2 플러그인 설치

Marketplace를 추가한 후 개별 플러그인을 설치합니다:

```
/plugin install msbaek-tdd@msbaek-claude-plugins
```

형식: `/plugin install <plugin-name>@<marketplace-name>`

### 4.3 플러그인 활성화 확인

설치 후 플러그인이 활성화되었는지 확인합니다:

```
/plugin list
```

비활성화된 경우 활성화:

```
/plugin enable msbaek-tdd@msbaek-claude-plugins
```

### 4.4 사용법

설치 완료 후 다음 Skill들을 사용할 수 있습니다:

| 명령어 | 설명 |
|--------|------|
| `/tdd general com.example.bowling.BowlingGame` | General TDD 프로젝트 생성 |
| `/tdd web-usecase com.example.order.CreateOrder` | Web Usecase TDD 프로젝트 생성 |
| `/tdd-plan [plan-doc-path]` | SRS, 예제, 테스트 목록 작성 |
| `/tdd-rgb [plan-doc-path]` | Red-Green-Blue 사이클 실행 |

### 4.5 전체 설치 과정 요약

```
# 1. Marketplace 추가
/plugin marketplace add msbaek/msbaek-claude-plugins

# 2. 플러그인 설치
/plugin install msbaek-tdd@msbaek-claude-plugins

# 3. 새 세션 시작 후 사용
/tdd general com.example.bowling.BowlingGame
```

---

## 5. 플러그인 업데이트

### 5.1 개발자 (배포자)

플러그인을 수정한 후 GitHub에 Push하면 됩니다:

```bash
cd ~/git/msbaek-claude-plugins

# 파일 수정 후
git add .
git commit -m "feat: improve tdd-red agent"
git push origin main
```

**버전 관리 시:**

1. `msbaek-tdd/.claude-plugin/plugin.json`의 `version` 업데이트
2. `.claude-plugin/marketplace.json`의 해당 플러그인 `version` 업데이트
3. Commit & Push

### 5.2 사용자 (설치자)

```
# Marketplace 업데이트 (최신 카탈로그 가져오기)
/plugin marketplace update msbaek-claude-plugins

# 플러그인 업데이트
/plugin update msbaek-tdd@msbaek-claude-plugins
```

---

## 6. 검증 및 테스트

### 6.1 Marketplace 검증

```bash
# CLI에서 검증
claude plugin validate .

# 또는 Claude Code 내에서
/plugin validate .
```

### 6.2 로컬 테스트

배포 전 로컬에서 전체 흐름을 테스트합니다:

```
# 1. 로컬 Marketplace 추가
/plugin marketplace add ./path/to/msbaek-claude-plugins

# 2. 플러그인 설치
/plugin install msbaek-tdd@msbaek-claude-plugins

# 3. Skill 동작 확인
/tdd general com.example.bowling.BowlingGame
```

### 6.3 검증 체크리스트

- [ ] `marketplace.json` JSON 문법 유효
- [ ] 모든 플러그인 `source` 경로가 올바름
- [ ] 각 Skill의 SKILL.md frontmatter에 `name`, `description` 존재
- [ ] 각 Agent의 .md frontmatter에 `name`, `description`, `tools` 존재
- [ ] `/tdd`, `/tdd-plan`, `/tdd-rgb` 명령어가 인식됨
- [ ] Agent 위임이 정상 동작

---

## 7. 팀 배포 설정

### 7.1 프로젝트별 자동 설치 안내

팀 프로젝트의 `.claude/settings.json`에 Marketplace를 추가하면, 팀원이 프로젝트를 열 때 자동으로 설치를 안내받습니다:

```json
{
  "extraKnownMarketplaces": {
    "msbaek-claude-plugins": {
      "source": {
        "source": "github",
        "repo": "msbaek/msbaek-claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "msbaek-tdd@msbaek-claude-plugins": true
  }
}
```

### 7.2 Private 저장소 인증

Private 저장소를 사용하는 경우:

**수동 설치 시:** 기존 Git 자격 증명이 사용됩니다. `git clone`이 작동하면 Claude Code에서도 작동합니다.

**자동 업데이트 설정:**

```bash
# GitHub
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# GitLab
export GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
```

Shell 설정 파일(`.zshrc` 등)에 추가하여 영구 설정합니다.

---

## 8. 트러블슈팅

### Marketplace를 추가할 수 없음

| 원인 | 해결 |
|------|------|
| URL에 접근 불가 | 저장소가 public인지, 인증이 설정되었는지 확인 |
| marketplace.json 없음 | `.claude-plugin/marketplace.json` 경로 확인 |
| JSON 문법 오류 | `claude plugin validate .` 실행 |

### 플러그인이 설치되지 않음

| 원인 | 해결 |
|------|------|
| source 경로 오류 | marketplace.json의 `source` 경로가 실제 디렉토리를 가리키는지 확인 |
| plugin.json 없음 | 플러그인 디렉토리에 `.claude-plugin/plugin.json` 존재 확인 |
| 외부 파일 참조 | 플러그인은 캐시로 복사되므로 `../` 경로 사용 불가. 심링크 또는 디렉토리 재구성 필요 |

### Skill이 인식되지 않음

| 원인 | 해결 |
|------|------|
| 플러그인 비활성화 | `/plugin list`로 확인, `/plugin enable` 실행 |
| frontmatter 오류 | SKILL.md의 YAML frontmatter에 `name` 필드 확인 |
| 세션 미갱신 | 새 Claude Code 세션 시작 |

---

## 참고 자료

- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) - 공식 문서
- [Create plugins](https://code.claude.com/docs/en/plugins) - 플러그인 생성 가이드
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) - 기술 사양
- [Discover and install prebuilt plugins](https://code.claude.com/docs/en/discover-plugins) - 플러그인 설치
