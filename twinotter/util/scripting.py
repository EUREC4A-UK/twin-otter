import re


def parse_docopt_arguments(function, __doc__):
    """

    Args:
        function:
        __doc__: The docstring of the function being parsed

    Returns:

    """
    # Load in the arguments
    import docopt

    arguments = docopt.docopt(__doc__)

    # Remove the help argument
    del arguments["--help"]

    # Parse the remaining arguments
    parsed_arguments = {}
    for arg in arguments.keys():
        # Arguments specified as all upper case (<ARG>)
        if arg.upper() == arg:
            newarg = arg
        # Arguments specified in angle brackets (<arg>)
        elif re.match(r"<(.*)>", arg):
            newarg = re.match(r"<(.*)>", arg).groups()[0]
        # Arguments specificied with dashes (-arg | --arg)
        elif re.match(r"-+(.*)", arg):
            newarg = re.match(r"-+(.*)", arg).groups()[0]
        else:
            raise KeyError("Couldn't parse argument {}".format(arg))

        parsed_arguments[newarg] = arguments[arg]

    # Call the function and return
    return function(**parsed_arguments)
