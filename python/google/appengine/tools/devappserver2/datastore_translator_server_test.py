"""Tests for the datastore translator server.

These tests are a bit weird: they were written when we were writing our own
implementation of the translator, then modified to work against the stub's
implementation.  The coverage is thus pretty inconsistent, but hopefully good
enough.

Also useful are the google-cloud-python system tests.  To run these:
- clone https://github.com/googleapis/google-cloud-python
- apply some patches to get system tests running against the emulator:
    https://github.com/googleapis/google-cloud-python/compare/master...Khan:benkraft.system-tests-on-emulator
  TODO(benkraft): see if upstream wants these.
- in frankenserver root, run a dev_appserver instance:
    python/dev_appserver.py --enable_datastore_translator=true \
      --dev_appserver_log_level=debug -A testytest --clear_datastore \
      python/demos/python/guestbook/app.yaml
- in google-cloud-python/datastore, run the tests:
    DATASTORE_EMULATOR_HOST=localhost:8001 DATASTORE_DATASET=testytest \
      GOOGLE_APPLICATION_CREDENTIALS=/dev/null GOOGLE_CLOUD_DISABLE_GRPC=1 \
      nox -s system-3.7 -- --tb=native
At present, test_all_value_types fails (due to inconsistent rules about
indexing entity properties in the datastore_v1 and datastore_v3), and
test_query_offset_timestamp_keys is somewhat flaky (for unknown reasons).
"""
from __future__ import absolute_import

import base64
import cStringIO
import json
import os
import wsgiref.util

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import db
from google.appengine.tools.devappserver2 import datastore_translator_server
from google.appengine.tools.devappserver2 import stub_util
from google.appengine.tools.devappserver2 import wsgi_test_utils


# TODO(benkraft): Write instructions for running the google-cloud-python system
# tests against the translator.
class DatastoreTranslatorHandlerTestBase(wsgi_test_utils.WSGITestCase):
  maxDiff = None

  # In general, consistency guarantees are on the caller, and not our problem,
  # so we make everything consistent to simplify tests.  But callers can set
  # the consistency, if they need to test consistency-related behavior itself!
  def setUp(self, datastore_consistency_probability=1.0):
    super(DatastoreTranslatorHandlerTestBase, self).setUp()
    self.app_id = 'dev~myapp'
    # TODO(benkraft): Clean this environ setting up at end-of-test.
    # (Many of the devappserver tests don't do this, so it can't be that
    # important.)
    os.environ['APPLICATION_ID'] = self.app_id
    consistency_policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
      probability=datastore_consistency_probability)
    stub_util.setup_test_stubs(
      app_id=self.app_id,
      datastore_consistency=consistency_policy,
    )
    self.server = datastore_translator_server.get_app('localhost')

  def _strip_untested_fields(self, json_response):
    if isinstance(json_response, dict):
      json_response.pop('version', None)
      map(self._strip_untested_fields, json_response.values())
    elif isinstance(json_response, list):
      map(self._strip_untested_fields, json_response)
    return json_response

  def getJsonResponse(self, relative_url, json_request, expected_status):
    # Build the fake request (partially cribbed from api_server_test.py).
    request_body = json.dumps(json_request)
    request_environ = {
      'HTTP_HOST': 'localhost:8001',
      'PATH_INFO': relative_url,
      'REQUEST_METHOD': 'POST',
      'CONTENT_TYPE': 'application/json',
      'CONTENT_LENGTH': str(len(request_body)),
      'wsgi.input': cStringIO.StringIO(request_body),
    }
    wsgiref.util.setup_testing_defaults(request_environ)

    # Set up the WSGI response callable.
    # cribbed from wsgi_test_utils.py, but modified to allow us to assert about
    # the *parsed* json:
    write_buffer = cStringIO.StringIO()
    actual_start_response_args = []

    def start_response(status, headers, exc_info=None):
      actual_start_response_args.extend((status, headers, exc_info))
      return write_buffer.write

    # Run the request.
    response = self.server(request_environ, start_response)

    # Assert that we got a response and it looks as expected.
    self.assertTrue(actual_start_response_args,
                    "start_response never called!")
    self.assertEqual(len(actual_start_response_args), 3,
                     "start_response called multiple times!")

    actual_status, actual_headers, actual_exc_info = actual_start_response_args
    actual_status_int = int(actual_status.split()[0])
    response_body = ''.join(response)

    self.assertEqual(expected_status, actual_status_int,
                     "Expected status %s, got status %s for response %s"
                     % (expected_status, actual_status_int, response_body))
    self.assertIsNone(actual_exc_info)

    try:
      return json.loads(response_body)
    except Exception:
      print response_body
      raise

  def assertOK(self, relative_url, json_request, expected_json_response):
    actual_response = self.getJsonResponse(relative_url, json_request, 200)
    self.assertEqual(self._strip_untested_fields(actual_response),
                     expected_json_response)

  def assertError(self, relative_url, json_request,
                  expected_http_status, expected_grpc_status):
    actual_response = self.getJsonResponse(relative_url, json_request,
                                           expected_http_status)
    # We deliberately don't assert about the message, since that seems likely
    # to be fragile.
    self.assertIn('error', actual_response)
    self.assertEqual(actual_response['error']['code'], expected_http_status)
    self.assertEqual(actual_response['error']['status'], expected_grpc_status)


class TestAllocateIds(DatastoreTranslatorHandlerTestBase):
  def test_success_simple_key(self):
    self.assertOK(
      '/v1/projects/myapp:allocateIds',
      {'keys': [{
        'path': [{'kind': 'Foo'}]
      }]},
      {'keys': [{
        'partitionId': {'projectId': 'myapp'},
        # Conveniently (here and below), the sqlite stub seems to be totally
        # deterministic as to which ID it allocates us (namely 1).
        'path': [{'kind': 'Foo', 'id': '5629499534213120'}]
      }]})

  def test_success_several_keys(self):
    self.assertOK(
      '/v1/projects/myapp:allocateIds',
      {'keys': [
        {'path': [{'kind': 'Foo'}]},
        {'path': [{'kind': 'Foo'}]},
        {'path': [{'kind': 'Foo'}]},
        {'path': [{'kind': 'Foo'}]},
        {'path': [{'kind': 'Bar'}]},
      ]},
      {'keys': [
        {
          'partitionId': {'projectId': 'myapp'},
          'path': [{'kind': 'Foo', 'id': '5629499534213120'}]
        },
        {
          'partitionId': {'projectId': 'myapp'},
          'path': [{'kind': 'Foo', 'id': '5066549580791808'}]
        },
        {
          'partitionId': {'projectId': 'myapp'},
          'path': [{'kind': 'Foo', 'id': '6192449487634432'}]
        },
        {
          'partitionId': {'projectId': 'myapp'},
          'path': [{'kind': 'Foo', 'id': '4785074604081152'}]
        },
        {
          'partitionId': {'projectId': 'myapp'},
          # Again, this is arbitrary but deterministic.
          'path': [{'kind': 'Bar', 'id': '5910974510923776'}]
        },
      ]})

  def test_success_with_ancestors(self):
    self.assertOK(
      '/v1/projects/myapp:allocateIds',
      {'keys': [{
        'path': [
          {'kind': 'Foo', 'id': '5629499534213120'},
          {'kind': 'Bar', 'name': 'asdfgh1234'},
          {'kind': 'Baz'},
        ],
      }]},
      {'keys': [{
        'partitionId': {'projectId': 'myapp'},
        'path': [
          {'kind': 'Foo', 'id': '5629499534213120'},
          {'kind': 'Bar', 'name': 'asdfgh1234'},
          {'kind': 'Baz', 'id': '5629499534213120'},
        ],
      }]})

  def test_success_with_namespace(self):
    self.assertOK(
      '/v1/projects/myapp:allocateIds',
      {'keys': [{
        'partitionId': {
          'projectId': 'myapp',
          'namespaceId': 'the-namespace',
        },
        'path': [{'kind': 'Foo'}],
      }]},
      {'keys': [{
        'partitionId': {
          'projectId': 'myapp',
          'namespaceId': 'the-namespace',
        },
        'path': [{'kind': 'Foo', 'id': '5629499534213120'}]
      }]})

  def test_empty_success(self):
    self.assertOK(
      '/v1/projects/myapp:allocateIds',
      {},
      {})
    self.assertOK(
      '/v1/projects/myapp:allocateIds',
      {'keys': []},
      {})

  def test_no_kind(self):
    self.assertError(
      '/v1/projects/myapp:allocateIds',
      {'keys': [{'path': [{}]}]},
      400, 'INVALID_ARGUMENT')

  def test_mismatched_project(self):
    self.assertError(
      '/v1/projects/myapp:allocateIds',
      {'keys': [{
        'partitionId': {'projectId': 'yourapp'},
        'path': [{'kind': 'Foo'}],
      }]},
      400, 'INVALID_ARGUMENT')

  def test_matched_but_wrong_project(self):
    self.assertError(
      '/v1/projects/yourapp:allocateIds',
      {'keys': [{
        'partitionId': {'projectId': 'yourapp'},
        'path': [{'kind': 'Foo'}],
      }]},
      400, 'INVALID_ARGUMENT')


class SimpleModel(db.Model):
  boolean = db.BooleanProperty(indexed=True)
  integer = db.IntegerProperty(indexed=True)
  unindexed_string = db.StringProperty(indexed=False)
  indexed_string = db.StringProperty(indexed=True)
  byte_string = db.ByteStringProperty(indexed=True)


class OtherModel(db.Model):
  boolean = db.BooleanProperty(indexed=True)


class TestLookup(DatastoreTranslatorHandlerTestBase):
  def setUp(self):
    super(TestLookup, self).setUp()

    SimpleModel(
      key_name='exists',
      boolean=True,
      integer=12,
      unindexed_string=u'\u1111',
      byte_string='\x80',
    ).put()

    SimpleModel(
      parent=db.Key.from_path('ParentModel', 1),
      key_name='child',
      boolean=False,
      integer=16,
      unindexed_string=u'\u2222',
      byte_string='\x80',
    ).put()

  def test_success_simple_key(self):
    self.assertOK(
      '/v1/projects/myapp:lookup',
      {'keys': [{'path': [{'kind': 'SimpleModel', 'name': 'exists'}]}]},

      {
        'found': [{
          'entity': {
            'key': {
              'partitionId': {'projectId': 'myapp'},
              'path': [{'kind': 'SimpleModel', 'name': 'exists'}],
            },
            'properties': {
              'byte_string': {'blobValue': 'gA=='},
              'boolean': {'booleanValue': True},
              'integer': {'integerValue': '12'},
              'indexed_string': {'nullValue': None},
              'unindexed_string': {
                'excludeFromIndexes': True,
                'stringValue': u'\u1111',
              },
            },
          },
        }],
      })

  def test_missing(self):
    self.assertOK(
      '/v1/projects/myapp:lookup',
      {'keys': [{'path': [{'kind': 'SimpleModel', 'name': 'nope'}]}]},

      {
        'missing': [{
          'entity': {
            'key': {
              'partitionId': {'projectId': 'myapp'},
              'path': [{'kind': 'SimpleModel', 'name': 'nope'}],
            },
          },
        }],
      })

  def test_several_keys(self):
    self.assertOK(
      '/v1/projects/myapp:lookup',
      {'keys': [
        {'path': [{'kind': 'SimpleModel', 'name': 'exists'}]},
        {'path': [{'kind': 'SimpleModel', 'name': 'nope'}]},
        {'path': [
          {'kind': 'ParentModel', 'id': '1'},
          {'kind': 'SimpleModel', 'name': 'child'},
        ]},
      ]},

      {
        'found': [{
          'entity': {
            'key': {
              'partitionId': {'projectId': 'myapp'},
              'path': [{'kind': 'SimpleModel', 'name': 'exists'}],
            },
            'properties': {
              'byte_string': {'blobValue': 'gA=='},
              'boolean': {'booleanValue': True},
              'integer': {'integerValue': '12'},
              'indexed_string': {'nullValue': None},
              'unindexed_string': {
                'excludeFromIndexes': True,
                'stringValue': u'\u1111',
              },
            },
          },
        }, {
          'entity': {
            'key': {
              'partitionId': {'projectId': 'myapp'},
              'path': [
                {'kind': 'ParentModel', 'id': '1'},
                {'kind': 'SimpleModel', 'name': 'child'},
              ],
            },
            'properties': {
              'byte_string': {'blobValue': 'gA=='},
              'boolean': {'booleanValue': False},
              'integer': {'integerValue': '16'},
              'indexed_string': {'nullValue': None},
              'unindexed_string': {
                'excludeFromIndexes': True,
                'stringValue': u'\u2222',
              },
            },
          },
        }],
        'missing': [{
          'entity': {
            'key': {
              'partitionId': {'projectId': 'myapp'},
              'path': [{'kind': 'SimpleModel', 'name': 'nope'}],
            },
          },
        }],
      })

  def test_empty_success(self):
    self.assertOK(
      '/v1/projects/myapp:lookup',
      {},
      {})
    self.assertOK(
      '/v1/projects/myapp:lookup',
      {'keys': []},
      {})

  def test_errors_on_unknown_option(self):
    self.assertError(
      '/v1/projects/myapp:lookup',
      {
        'keys': [{'path': [{'kind': 'SimpleModel', 'name': 'exists'}]}],
        'readOptions': {'garbage': 'yes please'},
      },
      400, 'INVALID_ARGUMENT')


class TestRunQuery(DatastoreTranslatorHandlerTestBase):
  def setUp(self):
    super(TestRunQuery, self).setUp()

    SimpleModel(
      key_name='exists',
      boolean=True,
      integer=12,
      indexed_string=u'\u1111',
      byte_string='\x80',
    ).put()

    SimpleModel(
      key_name='empty',
    ).put()

    SimpleModel(
      parent=db.Key.from_path('ParentModel', 1),
      key_name='child',
      boolean=False,
      integer=16,
      indexed_string=u'\u2222',
      byte_string='\x80',
    ).put()

    SimpleModel(
      parent=db.Key.from_path('ParentModel', 1),
      key_name='child2',
      boolean=False,
      integer=17,
      indexed_string=u'\u2222',
      byte_string='\x83',
    ).put()

    SimpleModel(
      parent=db.Key.from_path('ParentModel', 2),
      key_name='child3',
      boolean=False,
      integer=18,
      indexed_string=u'\u2222',
      byte_string='\x82',
    ).put()

    OtherModel(
      parent=db.Key.from_path('ParentModel', 1),
      key_name='otherchild',
      boolean=False,
    ).put()

  def _assert_query_results(self, json_request, expected_key_names,
                            expected_result_type='FULL',
                            expected_more_results='MORE_RESULTS_AFTER_LIMIT'):
    """Assert that the given query returns certain result keys.

    For most of our tests, we just want to assert about query semantics; the
    exact output result is tested extensively in translate_entity_test.py, and
    in fact asserting about the cursors is pretty annoying because they're
    opaque values to us.  (Luckily, they're deterministic, at least on dev.)
    So we use this helper, which just asserts the parts we want.
    """
    relative_url = '/v1/projects/myapp:runQuery'
    actual_response = self.getJsonResponse(relative_url, json_request, 200)

    # Assert about various toplevel metadata
    self.assertEqual(
      actual_response['batch']['entityResultType'],
      expected_result_type)
    self.assertEqual(
      actual_response['batch']['moreResults'],
      expected_more_results)
    # We can do this one consistency check on the cursors; the rest we leave to
    # test_cursors.
    if actual_response['batch']['entityResults']:
      self.assertEqual(
        actual_response['batch']['endCursor'],
        actual_response['batch']['entityResults'][-1]['cursor'])

    # Assert about the returned entities.
    # We only care about the order in some cases, but it's always deterministic
    # in test-land at least (it's an order by key, I think), so we just assert
    # about it always.
    self.assertEqual(
      [entity_result['entity']['key']['path'][-1]['name']
       for entity_result in actual_response['batch']['entityResults']],
      expected_key_names)
    for entity_result in actual_response['batch']['entityResults']:
      self.assertTrue(entity_result['cursor'])
      self.assertTrue(entity_result['version'])

  def test_simple_query(self):
    # Here, we test the whole query result, to make sure it looks as expected.
    self.assertOK(
      '/v1/projects/myapp:runQuery',
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'integer'},
              'op': 'EQUAL',
              'value': {'integerValue': '12'},
            },
          },
        },
      },

      {
        'batch': {
          'entityResultType': 'FULL',
          'entityResults': [
            {
              'entity': {
                'key': {
                  'partitionId': {'projectId': 'myapp'},
                  'path': [{'kind': 'SimpleModel', 'name': 'exists'}],
                },
                'properties': {
                  'boolean': {'booleanValue': True},
                  'byte_string': {'blobValue': 'gA=='},
                  'indexed_string': {
                    'stringValue': u'\u1111',
                  },
                  'integer': {'integerValue': '12'},
                  'unindexed_string': {
                    'nullValue': None,
                    'excludeFromIndexes': True,
                  },
                },
              },
              'cursor':
              'CioSJGoJZGV2fm15YXBwchcLEgtTaW1wbGVNb2RlbCIGZXhpc3RzDBgAIAA=',
            },
          ],
          'endCursor':
          'CioSJGoJZGV2fm15YXBwchcLEgtTaW1wbGVNb2RlbCIGZXhpc3RzDBgAIAA=',
          'moreResults': 'MORE_RESULTS_AFTER_LIMIT',
        },
      })

    # Test the same query, using _assert_query_results, for documentation.
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'integer'},
              'op': 'EQUAL',
              'value': {'integerValue': '12'},
            },
          },
        },
      },
      ['exists'])

  def test_projection_query(self):
    self.assertOK(
      '/v1/projects/myapp:runQuery',
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'integer'},
              'op': 'GREATER_THAN_OR_EQUAL',
              'value': {'integerValue': '12'},
            },
          },
          'order': [
            {'property': {'name': 'integer'}},
          ],
          'limit': 1,
          'projection': [
            {'property': {'name': 'boolean'}},
            {'property': {'name': 'integer'}},
          ],
        },
      },

      {
        'batch': {
          'entityResultType': 'PROJECTION',
          'entityResults': [
            {
              'entity': {
                'key': {
                  'partitionId': {'projectId': 'myapp'},
                  'path': [{'kind': 'SimpleModel', 'name': 'exists'}],
                },
                'properties': {
                  'boolean': {'booleanValue': True, 'meaning': 18},
                  'integer': {'integerValue': '12', 'meaning': 18},
                },
              },
              'cursor': ('CkgKDQoHaW50ZWdlchICCAwKDQoHYm9vbGVhbhICEAESJGoJZGV2'
                         'fm15YXBwchcLEgtTaW1wbGVNb2RlbCIGZXhpc3RzDBgAIAA='),
            },
          ],
          'endCursor': ('CkgKDQoHaW50ZWdlchICCAwKDQoHYm9vbGVhbhICEAESJGoJZGV2'
                        'fm15YXBwchcLEgtTaW1wbGVNb2RlbCIGZXhpc3RzDBgAIAA='),
          'moreResults': 'MORE_RESULTS_AFTER_LIMIT',
        },
      })

  def test_keys_only_query(self):
    self.assertOK(
      '/v1/projects/myapp:runQuery',
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'integer'},
              'op': 'LESS_THAN_OR_EQUAL',
              'value': {'integerValue': '12'},
            },
          },
          'projection': [{'property': {'name': '__key__'}}],
        },
      },

      {
        'batch': {
          'entityResultType': 'KEY_ONLY',
          'entityResults': [
            {
              'entity': {
                'key': {
                  'partitionId': {'projectId': 'myapp'},
                  'path': [{'kind': 'SimpleModel', 'name': 'empty'}],
                },
              },
              'cursor': ('CjYKCwoHaW50ZWdlchIAEiNqCWRldn5teWFwcHIWCxILU2ltcGx'
                         'lTW9kZWwiBWVtcHR5DBgAIAA='),
            }, {
              'entity': {
                'key': {
                  'partitionId': {'projectId': 'myapp'},
                  'path': [{'kind': 'SimpleModel', 'name': 'exists'}],
                },
              },
              'cursor': ('CjkKDQoHaW50ZWdlchICCAwSJGoJZGV2fm15YXBwchcLEgtTaW1'
                         'wbGVNb2RlbCIGZXhpc3RzDBgAIAA='),
            },
          ],
          'endCursor': ('CjkKDQoHaW50ZWdlchICCAwSJGoJZGV2fm15YXBwchcLEgtTaW1'
                        'wbGVNb2RlbCIGZXhpc3RzDBgAIAA='),
          'moreResults': 'MORE_RESULTS_AFTER_LIMIT',
        },
      })

  def test_string_filter(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'indexed_string'},
              'op': 'EQUAL',
              'value': {'stringValue': u'\u1111'},
            },
          },
        },
      },
      ['exists'])

  def test_byte_string_filter(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'byte_string'},
              'op': 'EQUAL',
              'value': {'blobValue': base64.b64encode('\x80')},
            },
          },
        },
      },
      ['child', 'exists'])

  def test_inequality_filter(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'integer'},
              'op': 'GREATER_THAN_OR_EQUAL',
              'value': {'integerValue': '17'},
            },
          },
        },
      },
      ['child2', 'child3'])

  def test_key_filter(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': '__key__'},
              'op': 'EQUAL',
              'value': {
                'keyValue': {
                  'path': [
                    {'kind': 'ParentModel', 'id': '1'},
                    {'kind': 'SimpleModel', 'name': 'child2'},
                  ],
                },
              },
            },
          },
        },
      },
      ['child2'])

  def test_key_inequality_filter(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': '__key__'},
              'op': 'GREATER_THAN',
              'value': {
                'keyValue': {
                  'path': [
                    {'kind': 'ParentModel', 'id': '1'},
                    {'kind': 'SimpleModel', 'name': 'child1'},
                  ],
                },
              },
            },
          },
        },
      },
      # The key ordering is
      # ParentModel, 1, SimpleModel, child
      # ParentModel, 1, SimpleModel, child2
      # ParentModel, 2, SimpleModel, child3
      # SimpleModel, empty
      # SimpleModel, exists
      ['child2', 'child3', 'empty', 'exists'])

  def test_key_ancestor_filter(self):
    # Ancestor can be the full path...
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': '__key__'},
              'op': 'HAS_ANCESTOR',
              'value': {
                'keyValue': {
                  'path': [
                    {'kind': 'ParentModel', 'id': '1'},
                    {'kind': 'SimpleModel', 'name': 'child2'},
                  ],
                },
              },
            },
          },
        },
      },
      ['child2'])

    # ...or a strict ancestor.
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': '__key__'},
              'op': 'HAS_ANCESTOR',
              'value': {
                'keyValue': {
                  'path': [
                    {'kind': 'ParentModel', 'id': '1'},
                  ],
                },
              },
            },
          },
        },
      },
      ['child', 'child2'])

  def test_multiple_filters(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'compositeFilter': {
              'op': 'AND',
              'filters': [
                {
                  'propertyFilter': {
                    'property': {'name': 'integer'},
                    'op': 'GREATER_THAN_OR_EQUAL',
                    'value': {'integerValue': '17'},
                  },
                }, {
                  'propertyFilter': {
                    'property': {'name': 'byte_string'},
                    'op': 'EQUAL',
                    'value': {'blobValue': base64.b64encode('\x82')},
                  },
                },
              ],
            },
          },
        },
      },
      ['child3'])

  def test_ordering(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'boolean'},
              'op': 'EQUAL',
              'value': {'booleanValue': False},
            },
          },
          'order': [{
            'property': {'name': 'byte_string'},
          }],
        },
      },
      ['child', 'child3', 'child2'])

  def test_reversed_ordering(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'boolean'},
              'op': 'EQUAL',
              'value': {'booleanValue': False},
            },
          },
          'order': [{
            'property': {'name': 'byte_string'},
            'direction': 'DESCENDING',
          }],
        },
      },
      ['child2', 'child3', 'child'])

  def test_multiple_orderings(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'order': [{
            'property': {'name': 'boolean'},
          }, {
            'property': {'name': 'byte_string'},
          }],
        },
      },
      # at least in sqlite, unset values apparently come first.
      ['empty', 'child', 'child3', 'child2', 'exists'])

  def test_ordering_offset(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'boolean'},
              'op': 'EQUAL',
              'value': {'booleanValue': False},
            },
          },
          'offset': 1,
          'order': [{
            'property': {'name': 'byte_string'},
          }],
        },
      },
      ['child3', 'child2'])

  def test_ordering_limit(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'boolean'},
              'op': 'EQUAL',
              'value': {'booleanValue': False},
            },
          },
          'limit': 2,
          'order': [{
            'property': {'name': 'byte_string'},
          }],
        },
      },
      ['child', 'child3'],
      expected_more_results='MORE_RESULTS_AFTER_LIMIT')

    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'boolean'},
              'op': 'EQUAL',
              'value': {'booleanValue': False},
            },
          },
          'limit': 5,
          'order': [{
            'property': {'name': 'byte_string'},
          }],
        },
      },
      ['child', 'child3', 'child2'])

  def test_ordering_offset_limit(self):
    self._assert_query_results(
      {
        'query': {
          'kind': [{'name': 'SimpleModel'}],
          'filter': {
            'propertyFilter': {
              'property': {'name': 'boolean'},
              'op': 'EQUAL',
              'value': {'booleanValue': False},
            },
          },
          'offset': 1,
          'limit': 1,
          'order': [{
            'property': {'name': 'byte_string'},
          }],
        },
      },
      ['child3'])

  def test_kindless_query(self):
    self._assert_query_results(
      {
        'query': {},
      },
      ['otherchild', 'child', 'child2', 'child3', 'empty', 'exists'])

  def test_cursors(self):
    entity_key_names = [
      'otherchild', 'child', 'child2', 'child3', 'empty', 'exists']

    # First, get all the entities with a kindless query.
    response = self.getJsonResponse(
      '/v1/projects/myapp:runQuery', {'query': {}}, 200)

    # Grab the returned cursors.
    entity_cursors = [entity_result['cursor']
                      for entity_result in response['batch']['entityResults']]
    entity_key_names = [
      entity_result['entity']['key']['path'][-1]['name']
      for entity_result in response['batch']['entityResults']]

    # Now, check that passing various cursor slices returns the corresponding
    # slice of entities.
    self._assert_query_results(
      {'query': {'startCursor': entity_cursors[1]}},
      # startCursor is an exclusive limit, so we start at index 2.
      entity_key_names[2:])
    self._assert_query_results(
      {'query': {'endCursor': entity_cursors[1]}},
      # endCursor, meanwhile, is inclusive.
      entity_key_names[:2],
      # The cloud datastore stub is wrong here: this should be
      # MORE_RESULTS_AFTER_CURSOR.  But it doesn't super matter.
      expected_more_results='MORE_RESULTS_AFTER_LIMIT')
    self._assert_query_results(
      {'query': {
        'startCursor': entity_cursors[0],
        'endCursor': entity_cursors[2],
      }},
      entity_key_names[1:3],
      # The cloud datastore stub is wrong here: this should be
      # MORE_RESULTS_AFTER_CURSOR.  But it doesn't super matter.
      expected_more_results='MORE_RESULTS_AFTER_LIMIT')
    self._assert_query_results(
      {'query': {
        'startCursor': entity_cursors[0],
        'limit': 1,
      }},
      entity_key_names[1:2],
      expected_more_results='MORE_RESULTS_AFTER_LIMIT')
    self._assert_query_results(
      {'query': {
        'startCursor': entity_cursors[0],
        'offset': 1,
        'limit': 1,
      }},
      entity_key_names[2:3],
      expected_more_results='MORE_RESULTS_AFTER_LIMIT')


class TestNontransactionalCommit(DatastoreTranslatorHandlerTestBase):
  def _entity(self, integer_value=12):
    return {
      'key': {
        'partitionId': {'projectId': 'myapp'},
        'path': [{'kind': 'SimpleModel', 'name': 'exists'}],
      },
      'properties': {
        'byte_string': {
          'blobValue': 'gA==',
        },
        'boolean': {'booleanValue': True},
        'integer': {'integerValue': str(integer_value)},
        'indexed_string': {'nullValue': None},
        'unindexed_string': {
          'excludeFromIndexes': True,
          'stringValue': u'\u1111',
        },
      }
    }

  def _insert_entity(self, integer_value=12):
    self.assertOK(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [{'insert': self._entity(integer_value)}]
      },
      {'indexUpdates': 9, 'mutationResults': [{}]})
    self._assert_entity_exists(integer_value)

  def _assert_entity_exists(self, expected_integer=12):
    self.assertOK(
      '/v1/projects/myapp:lookup',
      {'keys': [{'path': [{'kind': 'SimpleModel', 'name': 'exists'}]}]},
      {'found': [{'entity': self._entity(expected_integer)}]})

  def test_insert(self):
    self._insert_entity()

  def test_insert_conflict(self):
    self._insert_entity()
    self.assertError(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [{'insert': self._entity(12)}]
      }, 409, 'ALREADY_EXISTS')

  def test_upsert_new(self):
    self.assertOK(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [
          {
            'upsert': {
              'key': {'path': [{'kind': 'SimpleModel', 'name': 'exists'}]},
              'properties': {
                'byte_string': {
                  'blobValue': 'gA==',
                  'meaning': 16,
                },
                'boolean': {'booleanValue': True},
                'integer': {'integerValue': '13'},
                'indexed_string': {'nullValue': None},
                'unindexed_string': {
                  'excludeFromIndexes': True,
                  'stringValue': u'\u1111',
                },
              }
            }
          }
        ]
      },
      {'indexUpdates': 9, 'mutationResults': [{}]})
    self._assert_entity_exists(13)

  def test_upsert_existing(self):
    self._insert_entity(13)
    self._assert_entity_exists(13)
    self.assertOK(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [
          {
            'upsert': {
              'key': {'path': [{'kind': 'SimpleModel', 'name': 'exists'}]},
              'properties': {
                'byte_string': {
                  'blobValue': 'gA==',
                  'meaning': 16,
                },
                'boolean': {'booleanValue': True},
                'integer': {'integerValue': '14'},
                'indexed_string': {'nullValue': None},
                'unindexed_string': {
                  'excludeFromIndexes': True,
                  'stringValue': u'\u1111',
                },
              }
            }
          }
        ]
      },
      {'indexUpdates': 4, 'mutationResults': [{}]})
    self._assert_entity_exists(14)

  def test_update_existing(self):
    self._insert_entity(13)
    self._assert_entity_exists(13)
    self.assertOK(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [
          {
            'update': {
              'key': {'path': [{'kind': 'SimpleModel', 'name': 'exists'}]},
              'properties': {
                'byte_string': {'blobValue': 'gA=='},
                'boolean': {'booleanValue': True},
                'integer': {'integerValue': '14'},
                'indexed_string': {'nullValue': None},
                'unindexed_string': {
                  'excludeFromIndexes': True,
                  'stringValue': u'\u1111',
                },
              }
            }
          }
        ]
      },
      {'indexUpdates': 4, 'mutationResults': [{}]})
    self._assert_entity_exists(14)

  def test_update_missing(self):
    self.assertError(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [
          {
            'update': {
              'key': {'path': [{'kind': 'SimpleModel', 'name': 'exists'}]},
              'properties': {
                'byte_string': {'blobValue': 'gA=='},
                'boolean': {'booleanValue': True},
                'integer': {'integerValue': '14'},
                'indexed_string': {'nullValue': None},
                'unindexed_string': {
                  'excludeFromIndexes': True,
                  'stringValue': u'\u1111',
                },
              }
            }
          }
        ]
      }, 404, 'NOT_FOUND')

  def test_delete_existing(self):
    self._insert_entity(13)
    self._assert_entity_exists(13)
    self.assertOK(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [
          {
            'delete': {'path': [{'kind': 'SimpleModel', 'name': 'exists'}]},
          }
        ]
      },
      {'indexUpdates': 9, 'mutationResults': [{}]})

  def test_delete_missing(self):
    # Yes, delete is a silent no-op if the key is missing.
    self.assertOK(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [
          {
            'delete': {'path': [{'kind': 'SimpleModel', 'name': 'exists'}]},
          }
        ]
      },
      {'mutationResults': [{}]})

  def test_several_mutations(self):
    self.assertOK(
      '/v1/projects/myapp:commit',
      {
        'mode': 'NON_TRANSACTIONAL',
        'mutations': [
          {
            'insert': {
              # While we're at it, test with an incomplete key.
              'key': {'path': [{'kind': 'SimpleModel'}]},
              'properties': {'boolean': {'booleanValue': True}},
            },
          },
          {
            'upsert': {
              'key': {'path': [{'kind': 'SimpleModel', 'id': 17}]},
              'properties': {'boolean': {'booleanValue': True}},
            },
          },
        ]
      },
      {
        'mutationResults': [
          {
            'key': {
              'partitionId': {'projectId': 'myapp'},
              # This ID is auto-assigned, but seems to be deterministic.
              # (It's 0x14000000000000, so it's not "that" random.)
              'path': [{'kind': 'SimpleModel', 'id': '5629499534213120'}],
            },
          },
          {},
        ],
        'indexUpdates': 6,
      })
