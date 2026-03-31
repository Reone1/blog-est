---
title: "Best CLI Tools for Developers in 2026"
date: "2026-03-31"
type: "listicle"
description: "A curated list of 14 command-line tools that boost developer productivity in 2026, covering terminal emulators, git workflows, file management, system monitoring, and everyday productivity."
keywords: "best cli tools for developers 2026, developer tools, command line tools, terminal productivity"
---

# Best CLI Tools for Developers in 2026

<div class="tldr">

**TL;DR:** Modern CLI tools have replaced many legacy Unix utilities with faster, more intuitive alternatives. This list covers 14 tools across five categories: terminal emulators (Ghostty, WezTerm), git tools (lazygit, delta), file management (eza, fd, ripgrep, bat, fzf), productivity (zoxide, atuin, jq, yq), and monitoring (btop, k9s). Each entry includes install commands, key features, and practical usage examples.

</div>

## Why Upgrade Your CLI Toolkit

The command line remains the most efficient interface for many development tasks, but the standard tools shipped with most operating systems -- ls, find, grep, cat -- were designed decades ago. A new generation of CLI tools, mostly written in Rust and Go, offers significant improvements: better defaults, syntax highlighting, faster performance on large codebases, and more intuitive interfaces.

Adopting even a few of these tools can save minutes per day, which compounds into hours per month. Here are the 14 tools worth installing today.

## Terminal Emulators

### 1. Ghostty

Ghostty is a GPU-accelerated terminal emulator created by Mitchell Hashimoto (founder of HashiCorp). It is fast, standards-compliant, and has sensible defaults out of the box.

**Key features:**
- GPU-accelerated rendering with minimal latency
- Native tab and split support without a multiplexer
- Automatic font ligature support
- Cross-platform (macOS, Linux)
- Zero-configuration -- works well without a config file

**Install:**

```bash
# macOS
brew install ghostty

# Linux (Flatpak)
flatpak install com.mitchellh.ghostty
```

**Why it stands out:** Ghostty manages to be both feature-rich and simple. Unlike terminals that require extensive configuration to look and perform well, Ghostty's defaults are production-ready. Font rendering, color accuracy, and input latency are all excellent without touching a config file.

### 2. WezTerm

WezTerm is a GPU-accelerated terminal written in Rust with built-in multiplexing, configurable via Lua scripting.

**Key features:**
- Built-in multiplexer (splits, tabs, workspaces) -- no tmux needed
- Lua-based configuration for complex setups
- SSH integration with multiplexing
- Image rendering in the terminal (iTerm2 protocol, Sixel)
- Cross-platform (macOS, Linux, Windows)

**Install:**

```bash
# macOS
brew install wezterm

# Linux (AppImage)
curl -LO https://github.com/wez/wezterm/releases/latest/download/WezTerm-nightly.AppImage
chmod +x WezTerm-nightly.AppImage
```

**Why it stands out:** WezTerm's Lua configuration makes it exceptionally flexible. You can create dynamic tab titles, custom key bindings with conditional logic, and even integrate external APIs into your terminal status bar.

## Git Tools

### 3. lazygit

lazygit is a terminal UI for git that makes complex git operations visual and interactive.

**Key features:**
- Visual staging of individual lines and hunks
- Interactive rebase with drag-and-drop commit reordering
- Side-by-side diff viewing
- Conflict resolution with visual markers
- Custom commands and keybinding support

**Install:**

```bash
# macOS
brew install lazygit

# Linux
sudo apt install lazygit
# or
go install github.com/jesseduffield/lazygit@latest
```

**Usage:** Run `lazygit` in any git repository. Navigate with arrow keys. Press `space` to stage/unstage files, `c` to commit, `p` to push. The interactive rebase view (press `r` on the commits panel) lets you squash, edit, reorder, and drop commits visually.

**Why it stands out:** Operations like interactive rebase, cherry-picking across branches, and resolving merge conflicts become dramatically easier with a visual interface. Developers who switch to lazygit report spending 40-50% less time on git operations.

### 4. delta

delta is a syntax-highlighting pager for git diffs, blame, and grep output.

**Key features:**
- Language-aware syntax highlighting for diffs
- Side-by-side diff view
- Line numbers in diffs
- Hyperlinks to file paths (clickable in supported terminals)
- Git blame with syntax highlighting

**Install and configure:**

```bash
# Install
brew install git-delta   # macOS
sudo apt install git-delta  # Debian/Ubuntu

# Configure as default git pager
git config --global core.pager delta
git config --global interactive.diffFilter "delta --color-only"
git config --global delta.navigate true
git config --global delta.side-by-side true
```

**Why it stands out:** Standard git diff output is functional but hard to read, especially for large changes. delta transforms diffs into a format that is immediately scannable, with syntax highlighting that matches your editor's color scheme.

## File Management

### 5. eza

eza (successor to exa) is a modern replacement for `ls` with color coding, icons, git status integration, and tree view.

**Key features:**
- Color-coded file types and permissions
- Git status indicators next to each file
- Built-in tree view (replaces the `tree` command)
- Extended attribute and metadata display
- Header row for column identification

**Install:**

```bash
brew install eza        # macOS
sudo apt install eza    # Debian/Ubuntu
```

**Recommended aliases:**

```bash
alias ls="eza --icons --group-directories-first"
alias ll="eza -l --icons --group-directories-first --git"
alias tree="eza --tree --icons --level=3"
```

The `--git` flag shows the git status of each file inline, so you can see modified, staged, and untracked files at a glance when listing a directory.

### 6. fd

fd is a fast, user-friendly alternative to `find`.

**Key features:**
- Intuitive syntax (no `-name` or `-type f` boilerplate)
- Respects `.gitignore` by default
- Regular expression support
- Parallel execution of commands on results
- Smart case sensitivity (case-insensitive unless the pattern contains uppercase)

**Install:**

```bash
brew install fd         # macOS
sudo apt install fd-find  # Debian/Ubuntu (binary is `fdfind`)
```

**Usage comparison:**

```bash
# Find all Python files (traditional find)
find . -type f -name "*.py" -not -path "./.venv/*"

# Same thing with fd
fd -e py

# Find and delete all .pyc files
fd -e pyc -x rm {}

# Find files modified in the last hour
fd --changed-within 1h
```

### 7. ripgrep (rg)

ripgrep is the fastest grep tool available, with smart defaults for searching codebases.

**Key features:**
- 2-5x faster than grep on large codebases (benchmarked)
- Respects `.gitignore` automatically
- Searches compressed files
- Multi-line matching
- PCRE2 regex support
- File type filtering

**Install:**

```bash
brew install ripgrep    # macOS
sudo apt install ripgrep  # Debian/Ubuntu
```

**Usage:**

```bash
# Search for a function definition
rg "def process_payment" --type py

# Search with context (3 lines before and after)
rg "TODO|FIXME|HACK" -C 3

# Count matches per file
rg "import requests" --count

# Search only in specific file types, show line numbers
rg -n "SELECT.*FROM" --type sql --type py
```

### 8. bat

bat is a `cat` replacement with syntax highlighting, line numbers, and git integration.

**Key features:**
- Automatic syntax highlighting for 200+ languages
- Line numbers and grid decoration
- Git diff markers in the gutter
- Automatic paging for long files
- Can be used as a previewer for fzf

**Install:**

```bash
brew install bat        # macOS
sudo apt install bat    # Debian/Ubuntu (binary may be `batcat`)
```

**Usage:**

```bash
# View a file with syntax highlighting
bat src/main.rs

# Show only a range of lines
bat --line-range 50:75 config.yaml

# Use as a plain cat replacement (no decoration)
bat --plain data.json

# Concatenate multiple files with headers
bat src/*.py
```

### 9. fzf

fzf is a general-purpose fuzzy finder that integrates with nearly every CLI workflow.

**Key features:**
- Fuzzy matching on any list of items (files, processes, git branches, command history)
- Preview window with customizable commands
- Shell integration (Ctrl+R for history, Ctrl+T for files, Alt+C for directories)
- Composable with pipes

**Install:**

```bash
brew install fzf        # macOS
sudo apt install fzf    # Debian/Ubuntu

# Install shell integration
fzf --install
```

**Power-user configurations:**

```bash
# Use fd for file finding and bat for preview
export FZF_DEFAULT_COMMAND="fd --type f --hidden --follow --exclude .git"
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --line-range :500 {}'"

# Interactive git branch checkout
alias gcb="git branch --all | fzf --preview 'git log --oneline -20 {}' | xargs git checkout"

# Kill a process interactively
alias fkill="ps aux | fzf --header-lines=1 | awk '{print \$2}' | xargs kill"
```

## Productivity

### 10. zoxide

zoxide is a smarter `cd` command that learns your habits and lets you jump to directories with partial names.

**Key features:**
- Learns frequently visited directories
- Fuzzy matching on directory names
- Works across shell sessions
- Integrates with fzf for interactive selection

**Install:**

```bash
brew install zoxide     # macOS
sudo apt install zoxide # Debian/Ubuntu

# Add to .bashrc or .zshrc
eval "$(zoxide init zsh)"
```

**Usage:**

```bash
# Jump to a frequently visited directory
z projects    # cd to ~/code/projects (or wherever you go most often)
z api         # cd to ~/code/myapp/src/api

# Interactive selection when ambiguous
zi projects   # Opens fzf with matching directories
```

### 11. Atuin

Atuin replaces your shell history with a searchable, synchronized database.

**Key features:**
- Full-text search across shell history
- Sync history across multiple machines (end-to-end encrypted)
- Context-aware suggestions (filters by current directory, host, or session)
- Statistics on command usage
- Stores exit codes, duration, and working directory per command

**Install:**

```bash
bash <(curl --proto '=https' --tlsv1.2 -sSf https://setup.atuin.sh)
atuin register  # optional: sync across machines
atuin import auto  # import existing history
```

**Usage:** Press `Ctrl+R` and start typing. Atuin searches across your entire history with fuzzy matching, showing the directory and timestamp for each result. Filter by directory with `--cwd` or by exit status with `--exit 0` (only show successful commands).

### 12. jq and yq

jq processes JSON, yq processes YAML (and JSON, XML, TOML). Together they handle every configuration and API response format you will encounter.

**Install:**

```bash
brew install jq yq      # macOS
sudo apt install jq     # Debian/Ubuntu
pip install yq          # Python-based yq (wraps jq)
# or
brew install yq         # Go-based yq by Mike Farah
```

**Practical examples:**

```bash
# Extract specific fields from a JSON API response
curl -s https://api.github.com/repos/golang/go/releases/latest \
  | jq '{tag: .tag_name, date: .published_at, assets: [.assets[] | .name]}'

# Transform YAML (using Mike Farah's yq)
yq '.services.web.replicas = 3' docker-compose.yml

# Convert between formats
yq -o=json config.yaml | jq '.database.host'

# Filter an array
cat data.json | jq '[.users[] | select(.active == true) | {name, email}]'
```

## Monitoring

### 13. btop

btop is a resource monitor that combines the functionality of top, htop, and iostat into a single visually rich interface.

**Key features:**
- CPU, memory, disk, and network monitoring in one view
- Per-core CPU usage graphs with historical data
- Process tree view with sorting and filtering
- GPU monitoring support
- Mouse-clickable interface in the terminal
- Themes and customizable layout

**Install:**

```bash
brew install btop       # macOS
sudo apt install btop   # Debian/Ubuntu
```

btop displays CPU usage per core as a stacked graph, memory and swap as bar charts, disk I/O rates, network throughput, and a sortable process list -- all updating in real time. It replaces the need to switch between multiple monitoring tools.

### 14. k9s

k9s is a terminal UI for Kubernetes cluster management.

**Key features:**
- Real-time view of cluster resources (pods, deployments, services, nodes)
- Log streaming with search and filtering
- Shell into containers directly
- Resource editing in-place
- Port forwarding management
- Plugin system for custom commands

**Install:**

```bash
brew install k9s        # macOS
sudo apt install k9s    # Debian/Ubuntu (via snap or binary)
```

**Usage:** Run `k9s` to launch the UI. Type `:pods` to view pods, `:deploy` for deployments, `:svc` for services. Press `l` on a pod to stream logs, `s` to shell into it, `d` to describe it. Use `/` to filter resources by name.

k9s turns Kubernetes management from a series of memorized kubectl commands into a navigable, searchable interface. It is particularly valuable during incident response when you need to quickly inspect pod states, check logs, and restart services.

## Setting Up Your Toolkit

Here is a script to install all 14 tools on macOS:

```bash
brew install ghostty wezterm lazygit git-delta eza fd ripgrep bat fzf \
  zoxide atuin jq yq btop k9s

# Configure shell integrations
echo 'eval "$(fzf --zsh)"' >> ~/.zshrc
echo 'eval "$(zoxide init zsh)"' >> ~/.zshrc
echo 'eval "$(atuin init zsh)"' >> ~/.zshrc

# Set up git-delta
git config --global core.pager delta
git config --global delta.side-by-side true

# Add aliases
cat >> ~/.zshrc << 'ALIASES'
alias ls="eza --icons --group-directories-first"
alias ll="eza -l --icons --group-directories-first --git"
alias tree="eza --tree --icons --level=3"
alias cat="bat --plain"
ALIASES

source ~/.zshrc
```

And for Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y eza fd-find ripgrep bat fzf \
  zoxide jq btop lazygit git-delta

# Tools that need alternate install methods
go install github.com/jesseduffield/lazygit@latest
pip install yq
snap install k9s
bash <(curl --proto '=https' --tlsv1.2 -sSf https://setup.atuin.sh)
```

## The Compound Effect

No single tool on this list will transform your workflow overnight. But together, they eliminate dozens of small frictions: reading uncolored diffs, typing full directory paths, scrolling through unformatted command output, and memorizing obscure flag combinations.

The developers who are most productive at the command line are not the ones who memorize the most flags -- they are the ones who choose tools with better defaults. Every tool on this list works well out of the box. Install them, use them for a week, and the old tools will feel unbearably slow.
