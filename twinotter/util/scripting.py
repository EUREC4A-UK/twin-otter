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
        # Don't include arguments that have not been specified at the command line to
        # keep the default arguments defined by the function (docopt doesn't allow us
        # to specify default arguments unless it is part of the options list).
        if arguments[arg] is not None:
            # Arguments specified as all upper case (<ARG>)
            if arg.upper() == arg:
                newarg = arg.lower()
            # Arguments specified in angle brackets (<arg>)
            elif re.match(r"<(.*)>", arg):
                newarg = re.match(r"<(.*)>", arg).groups()[0]
            # Arguments specificied with dashes (-arg | --arg)
            elif re.match(r"-+(.*)", arg):
                newarg = re.match(r"-+(.*)", arg).groups()[0]
            # Arguments specified by their presence (True/False arguments)
            elif arguments[arg] is True or arguments[arg] is False:
                newarg = arg
            else:
                raise KeyError("Couldn't parse argument {}".format(arg))

            parsed_arguments[newarg] = arguments[arg]

    # Call the function and return
    return function(**parsed_arguments)
