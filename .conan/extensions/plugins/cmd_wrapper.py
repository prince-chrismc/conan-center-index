def cmd_wrapper(cmd, conanfile):
   if "cmake" in cmd:
       return 'echo "{}"'.format(cmd)
   return cmd
