conda_prefix = env("CONDA_PREFIX")
if_(conda_prefix == "test").then_(
	export("TEST_VARIABLE", path.join(env("CONDA_PREFIX"), "test/for/something"))
)
