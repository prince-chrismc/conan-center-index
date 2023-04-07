def cmd_wrapper(cmd, conanfile):
    if "cmake" in cmd:
        print(f'echo "{cmd}"')
    return cmd
