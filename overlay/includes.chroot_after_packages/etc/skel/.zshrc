# ===== MARK 42 shell (zsh) =====
# Commands change colour while you type:
#   blue   = the command / tool exists      red    = not found (typo or not installed)
#   blue bold = an existing folder (cd Documents)   underline = an existing file
#   yellow = text in quotes
# Colours: see ZSH_HIGHLIGHT_STYLES at the bottom.  Bash is still installed:
# type "bash" to use it, or "chsh -s /bin/bash" to make it your default again.

# ---- history
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=20000
setopt hist_ignore_dups hist_ignore_space hist_verify share_history extended_history

# ---- behaviour
setopt autocd interactive_comments no_beep numeric_glob_sort prompt_subst
WORDCHARS=${WORDCHARS//\/}        # Ctrl+W / Alt+Backspace stop at "/"

# ---- Tab completion (menu you can move through with the arrow keys)
autoload -Uz compinit && compinit -d ~/.cache/zcompdump
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'      # case-insensitive
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' rehash true                              # see newly installed tools
compdef _sudo mark 2>/dev/null                                  # complete after "mark" like after sudo

# ---- keys: Home / End / Delete / Ctrl+arrows, Up/Down search history by what you typed
bindkey -e
bindkey '^[[H' beginning-of-line   '^[[F' end-of-line   '^[[3~' delete-char
bindkey '^[[1;5C' forward-word     '^[[1;5D' backward-word
autoload -Uz up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search; zle -N down-line-or-beginning-search
bindkey '^[[A' up-line-or-beginning-search   '^[[B' down-line-or-beginning-search

# ---- colours for ls / grep
if command -v dircolors >/dev/null; then eval "$(dircolors -b)"; fi
alias ls='ls --color=auto' grep='grep --color=auto' ip='ip --color=auto'

# ---- prompt
if [[ $EUID -eq 0 ]]; then
  # full root mode (mark42): white-on-red banner stays red on purpose = "careful, root"
  PROMPT=$'%B%F{red}┌─%K{red}%F{15} MARK 42 :: ROOT %k%F{red}─[%b%F{7}%~%B%F{red}]\n└──# %f%b'
else
  PROMPT=$'%B%F{blue}┌─[%b%F{15}%n%B%F{blue}@%b%F{15}mark42%B%F{blue}]─[%b%F{7}%~%B%F{blue}]\n└──╼ %f%b'
fi

# ---- "mark" = sudo, "mark42" = full root shell (trailing space lets aliases work after them)
alias mark='mark '
alias sudo='sudo '
alias ll='ls -lah --color=auto'
alias update='mark apt update && mark apt full-upgrade'
# clean terminal: run "fastfetch" yourself to show the system logo/info

# ---- live command colours (must be loaded last)
# hex colours need a true-colour terminal (Konsole is one); elsewhere, e.g. the
# text console, map them to the nearest of 256 colours
[[ $COLORTERM == (truecolor|24bit) ]] || zmodload zsh/nearcolor 2>/dev/null
if [[ -r /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]]; then
  source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
  ZSH_HIGHLIGHT_HIGHLIGHTERS=(main brackets)
  ZSH_HIGHLIGHT_STYLES[command]='fg=#64b4ff,bold'
  ZSH_HIGHLIGHT_STYLES[builtin]='fg=#64b4ff,bold'
  ZSH_HIGHLIGHT_STYLES[alias]='fg=#64b4ff,bold'
  ZSH_HIGHLIGHT_STYLES[suffix-alias]='fg=#64b4ff,bold'
  ZSH_HIGHLIGHT_STYLES[function]='fg=#64b4ff,bold'
  ZSH_HIGHLIGHT_STYLES[hashed-command]='fg=#64b4ff,bold'
  ZSH_HIGHLIGHT_STYLES[precommand]='fg=#9fd4ff,bold,italic'
  ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#ff5f5f,bold'
  ZSH_HIGHLIGHT_STYLES[reserved-word]='fg=#c4a7ff'
  ZSH_HIGHLIGHT_STYLES[commandseparator]='fg=#7fa8cc'
  ZSH_HIGHLIGHT_STYLES[path]='fg=#e6e8ec,underline'
  ZSH_HIGHLIGHT_STYLES[path_prefix]='fg=#e6e8ec,underline'
  ZSH_HIGHLIGHT_STYLES[globbing]='fg=#56c8d8'
  ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#9fd4ff'
  ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#9fd4ff'
  ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#e6c07b'
  ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#e6c07b'
  ZSH_HIGHLIGHT_STYLES[dollar-quoted-argument]='fg=#e6c07b'
  ZSH_HIGHLIGHT_STYLES[back-quoted-argument]='fg=#56c8d8'
  ZSH_HIGHLIGHT_STYLES[redirection]='fg=#7fa8cc'
  ZSH_HIGHLIGHT_STYLES[comment]='fg=#6b7686,italic'
  ZSH_HIGHLIGHT_STYLES[arg0]='fg=#64b4ff,bold'

  # existing folders -> blue bold (wraps the plugin's own path check, so it stays
  # exactly as smart: ~, $VARS, relative paths, CDPATH, "cd" with no typo, ...)
  ZSH_HIGHLIGHT_STYLES[mark42-directory]='fg=#64b4ff,bold'
  ZSH_HIGHLIGHT_STYLES[autodirectory]='fg=#64b4ff,bold'
  if (( ${+functions[_zsh_highlight_main_highlighter_check_path]} )); then
    functions[_mark42_check_path_orig]=$functions[_zsh_highlight_main_highlighter_check_path]
    _zsh_highlight_main_highlighter_check_path() {
      _mark42_check_path_orig "$@" || return
      if [[ $REPLY == path ]]; then
        _zsh_highlight_main_highlighter_expand_path "$1"
        if [[ -d $REPLY ]]; then REPLY=mark42-directory; else REPLY=path; fi
      fi
      return 0
    }
  fi
fi
