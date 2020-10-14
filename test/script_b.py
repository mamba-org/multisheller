# if [ -z "$COMSPEC" ]; then
# 	export GEM_HOME=$CONDA_PREFIX/share/rubygems/
# 	export PATH="$CONDA_PREFIX/share/rubygems/bin:$PATH"
# else
# 	export GEM_HOME=$CONDA_PREFIX/Library/share/rubygems/
# 	export PATH="$CONDA_PREFIX/Library/share/rubygems/bin:$PATH"
# fi

if_(is_set(env("COMSPEC"))).then_([
	export("GEM_HOME", path.join(env("CONDA_PREFIX"), "Library/share/rubygems")),
	sys.path_prepend(path.join(env("CONDA_PREFIX"), "Library/share/rubygems/bin"))
]).else_([
	export("GEM_HOME", path.join(env("CONDA_PREFIX"), "/share/rubygems")),
	sys.path_prepend(path.join(env("CONDA_PREFIX"), "/share/rubygems/bin"))
])