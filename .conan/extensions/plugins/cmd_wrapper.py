def cmd_wrapper(cmd):
   if "cmake" in cmd:
       return 'echo "{}"'.format(cmd)
   return cmd
