from setuptools import setup, find_packages

setup(name="saaskit-subscription",
           version="0.1",
           description="Subscriptions based web app using django-paypal",
           author="SaaS kit",
           author_email="admin@saaskit.org",
           packages=find_packages(),
           include_package_data=True,
)

