from functools import wraps

from utils.utils_request import request_failed

MAX_CHAR_LENGTH = 255
STATE_LENGTH = 2500

# A decorator function for processing `require` in view function.
def CheckRequire(check_fn):
    @wraps(check_fn)
    def decorated(*args, **kwargs):
        try:
            return check_fn(*args, **kwargs)
        except Exception as e:
            # Handle exception e: KeyError(err_msg, err_code, status_code)
            error_code = 1 if len(e.args) < 2 else e.args[1]
            status_code = 400 if len(e.args) < 3 else e.args[2]
            return request_failed(error_code, e.args[0], status_code)  # Refer to below
    return decorated


# Here err_code == -2 denotes "Error in request body"
# And err_code == -1 denotes "Error in request URL parsing"
def require(body, key, type="string", err_msg=None, err_code=1, status_code=400, blank=False):
    
    if blank and (key not in body.keys() or body[key] == ""):
        return None
    
    if key not in body.keys():
        raise KeyError(err_msg if err_msg is not None 
                       else f"Invalid parameters. Expected `{key}`, but not found.", err_code, status_code)
    
    val = body[key]
    
    err_msg = f"Invalid parameters. Expected `{key}` to be `{type}` type."\
                if err_msg is None else err_msg
    
    if type == "int":
        try:
            val = int(val)
            return val
        except:
            raise KeyError(err_msg, err_code, status_code)
    
    elif type == "float":
        try:
            val = float(val)
            return val
        except:
            raise KeyError(err_msg, err_code, status_code)
    
    elif type == "string":
        try:
            val = str(val)
            return val
        except:
            raise KeyError(err_msg, err_code, status_code)
    
    elif type == "list":
        try:
            assert isinstance(val, list)
            return val
        except:
            raise KeyError(err_msg, err_code, status_code)
    
    elif type == "list[string]":
        try:
            assert isinstance(val, list)
            for i, ele in enumerate(val):
                val[i] = str(ele)
            return val
        except:
            raise KeyError(err_msg, err_code, status_code)

    else:
        raise NotImplementedError(f"Type `{type}` not implemented.", err_code, status_code)