import requests
import rollbar

from htk.lib.iterable.constants import *
from htk.lib.iterable.exceptions import *
from htk.utils import htk_setting

class IterableAPIClient(object):
    """
    https://api.iterable.com/api/docs
    """
    def __init__(self, api_key):
        self.api_key = api_key

    def get_resource_url(self, resource_type):
        """Returns the resource URL for `resource_type`
        """
        resource_path = ITERABLE_API_RESOURCES.get(resource_type)
        if resource_path is None:
            raise IterableAPIException('Invalid Iterable API resource: %s' % resource_type)

        url = '%s%s' % (
            ITERABLE_API_BASE_URL,
            resource_path,
        )
        return url

    def get(self, resource_type, params=None, headers=None):
        """Performs an Iterable API GET request
        """
        url = self.get_resource_url(resource_type)

        if params is None:
            params = {}

        params.update({
            'apiKey' : self.api_key,
        })

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            pass
        else:
            extra_data = {
                'response' : response.json()
            }
            rollbar.report_message('Unexpected response from Iterable API GET request', extra_data=extra_data)
        return response

    def post(self, resource_type, payload=None, params=None, headers=None):
        """Performs an Iterable API POST request
        """
        url = self.get_resource_url(resource_type)

        if params is None:
            params = {}
        params.update({
            'apiKey' : self.api_key,
        })

        response = requests.post(url, params=params, headers=headers, json=payload)
        if response.status_code == 200:
            pass
        else:
            extra_data = {
                'response' : response.json()
            }
            rollbar.report_message('Unexpected response from Iterable API POST request', extra_data=extra_data)
        return response

    def delete(self, resource_type, resource_params=None, params=None, headers=None):
        """Performs an Iterable API POST request
        """
        url = self.get_resource_url(resource_type)
        if resource_params:
            url = url % resource_params

        if params is None:
            params = {}
        params.update({
            'apiKey' : self.api_key,
        })

        response = requests.delete(url, params=params, headers=headers)
        if response.status_code == 200:
            pass
        else:
            extra_data = {
                'response' : response.json()
            }
            rollbar.report_message('Unexpected response from Iterable API DELETE request', extra_data=extra_data)
        return response

    ##
    # events

    def track_event(self, email, event_name, payload=None):
        """Track an event

        https://api.iterable.com/api/docs#!/events/track_post_1
        """
        if payload is None:
            payload = {}
        payload.update({
            'email' : email,
            'eventName' : event_name,
        })

        response = self.post('event_track', payload=payload)
        return response

    ##
    # users

    def delete_user(self, email):
        """Delete a user from Iterable

        https://api.iterable.com/api/docs#!/users/delete_delete_6
        """
        resource_params = {
            'email' : email,
        }
        response = self.delete('user_delete', resource_params=resource_params)
        return response

    ##
    # workflows

    def trigger_workflow(self, email, workflow_id, payload=None, list_id=None):
        """Trigger a workflow

        https://api.iterable.com/api/docs#!/workflows/triggerWorkflow_post_0
        """
        if payload is None:
            payload = {}
        payload.update({
            'email' : email,
            'workflowId' : workflow_id,
        })
        if list_id:
            payload['listId'] = list_id

        response = self.post('workflow_trigger', payload=payload)
        return response

class HtkIterableAPIClient(IterableAPIClient):
    """HTK-flavored Iterable API client

    This extends IterableAPIClient, which is more vanilla
    """

    def notify_sign_up(self, user):
        """Notify Iterable of a `user` sign up event

        Based on HTK settings, either track an event, trigger a workflow, or both
        """
        from htk.lib.iterable.utils import get_workflow_id
        sign_up_workflow_id = get_workflow_id('sign_up')
        if sign_up_workflow_id is not None:
            payload = {
                'dataFields' : {
                    'userId' : user.id,
                    'date_joined' : user.date_joined.strftime(ITERABLE_DATE_FORMAT),
                },
            }
            self.trigger_workflow(user.email, sign_up_workflow_id, payload=payload)

    def notify_account_activation(self, user):
        """Notify Iterable of a `user` activation event
        """
        from htk.lib.iterable.utils import get_workflow_id
        account_activation_workflow_id = get_workflow_id('account_activation')
        pass

    def notify_login(self, user):
        """Notify Iterable of a `user` login event
        """
        pass
