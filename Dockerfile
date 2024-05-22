#################################################################################
# Base image for Plotly Dash dashboard running on AWS Lambda
# 
# The context for building this image should be the root of the dashboard
# repository.  It MUST have the following files:
#
# - lambda_function.py: The Lambda handler function
# - requirements.txt: The Python dependencies for the dashboard
# - dash_app/: The directory containing the Dash app.
#
# The image produced by this file is set specifically to work with the lambda agent
# that is running in the container.  The WORKDIR (i.e., run dir of the container) is 
# /var/task.  The lambda_function.py, requirements.txt, and dash_app/ are copied there.
#
#################################################################################
# You can change to a different version of Python if needed
FROM public.ecr.aws/lambda/python:3.10

# Copy the user's python dependencies and install them
COPY requirements.txt .
RUN pip install -r requirements.txt

# Make sure to install apig-wsgi in order to bridge Lambda to Flask's wsgi interface.
RUN pip install apig-wsgi==2.18.0
COPY overwritten_apig_wsgi.py /var/lang/lib/python3.10/site-packages/apig_wsgi/__init__.py

# Copy application code.  If you have additional folders or files that are outside of
# the dash_app/ directory, you can copy them here.
COPY dash_app dash_app

# Copy lambda function
COPY lambda_function.py .

ENV PYTHONPATH "${PYTHONPATH}:${LAMBDA_TASK_ROOT}/dash_app"

# We need to set the command to tell the entrypoint script (i.e, the lambda agent) the 
# name of our handler module and method
CMD ["lambda_function.lambda_handler"]