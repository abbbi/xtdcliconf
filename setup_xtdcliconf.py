from cx_Freeze import setup, Executable

# https://github.com/anthony-tuininga/cx_Freeze/issues/209

productName = "xtdcliconf"

exe = Executable(
      script="xtdcliconf.py",
      targetName="xtdcliconf"
     )
setup(
      name="xtdcliconf",
      version="1.0",
      author="Michael Ablassmeier",
      executables=[exe],
      scripts=[
               'xtdcliconf.py'
               ]
      )
