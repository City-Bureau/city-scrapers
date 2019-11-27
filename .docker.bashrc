
userColor="\e[0;36m"
gitColor="\e[1;36m"
NC="\e[m"

PS1="$userColor(city-scrapers)$NC"
PS1="$PS1 \w"

# If in Git project, return name of branch
function pc {
    if [ -d .git ] || git rev-parse --git-dir > /dev/null 2>&1; then
        echo "($(git rev-parse --abbrev-ref HEAD)) "
    fi
}

# Combine everything together
PS1="$PS1 $gitColor\$(pc)$NC \n$> "

export CLICOLOR=1
export LSCOLORS=ExFxBxDxCxegedabagacad
if [ -x /usr/bin/dircolors ]; then
    alias ls='ls --color=auto'
    alias dir='dir --color=auto'
    alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

alias nano='nano -cT3'                      # Preferred 'nano' implementaion
alias la='ls -A'                            # la:       show all fils
alias which='type -all'                     # which:        Find executables
alias cp='cp -iv'                           # Preferred 'cp' implementation
alias mv='mv -iv'                           # Preferred 'mv' implementation
alias mkdir='mkdir -pv'                     # Preferred 'mkdir' implementation
alias ll='ls -FGlAhp'                       # Preferred 'ls' implementation
alias less='less -NFSRXc'                   # Preferred 'less' implementation
cd() { builtin cd "$@"; ls; }               # Always list directory contents upon 'cd'
alias cd..='cd ../'                         # Go back 1 directory level (for fast typers)