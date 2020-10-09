import sh

conda_prefix = sh.env("CONDA_PREFIX")

print(conda_prefix == "test")

print(sh.if_(conda_prefix == "test").then_(
	sh.export("TEST_VARIABLE", sh.path_join(sh.env("CONDA_PREFIX"), "test/for/something"))
))

