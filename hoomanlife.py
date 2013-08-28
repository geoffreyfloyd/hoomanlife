__all__ = ['main']

if __name__ == '__main__': # # if run as a script or by 'python -m hoomanlife'
    # we trigger the below "else" condition by the following import
    import hoomanlife
    hoomanlife.cmd.main()
else:
    # we are simply imported
    from _hoomanlife import cmd, controller, data, models, translation