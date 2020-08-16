import cx_Freeze

executables = [cx_Freeze.Executable("the_ball_app.py")]

cx_Freeze.setup(
    name="the Ball",
    options={"build_exe": {
        "packages" : ["pygame"], 
        "include_files":["img/"]
        } },
    executables = executables
    )