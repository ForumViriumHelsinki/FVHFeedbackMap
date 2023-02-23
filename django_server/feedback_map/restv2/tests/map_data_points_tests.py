import os

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from .base import FVHAPITestCase
from feedback_map import models
from feedback_map.rest.permissions import REVIEWER_GROUP


class MapDataPointsTests(FVHAPITestCase):
    def create_and_login_reviewer(self):
        user = User.objects.create(username='reviewer', first_name='Regina', last_name='Reviewer')
        user.groups.add(Group.objects.get_or_create(name=REVIEWER_GROUP)[0])
        self.client.force_login(user)
        return user

    def test_save_map_data_point(self):
        # Given that a user is signed in
        user = self.create_and_login_user()

        # When requesting to save an Map Data Point over ReST
        url = reverse('mapdatapoint-list')
        fields = {
            'lat': '60.16134701761975',
            'lon': '24.944593941327188',
            'comment': 'Nice view',
            'tags': ['Entrance', 'Steps']
        }
        response = self.client.post(url, data=fields, format='json')

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # And a note is created in db:
        note = models.MapDataPoint.objects.get()

        # And it registers the user as the creator of the note:
        self.assertEqual(note.created_by_id, user.id)
        self.assertEqual(note.modified_by_id, user.id)

        # And it creates any passed tags:
        self.assertSetEqual(set(note.tags), set(fields['tags']))

        # And when subsequently requesting to attach an image to the note
        with open(os.path.join(os.path.dirname(__file__), 'test_image.png'), 'rb') as file:
            file_content = file.read()
        uploaded_file = SimpleUploadedFile("image.png", file_content, content_type="image/png")
        url = reverse('mapdatapoint-detail', kwargs={'pk': note.id})
        response = self.client.patch(url, data={'image': uploaded_file}, format='multipart')

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And a note is updated in db:
        note = models.MapDataPoint.objects.get()
        self.assertEqual(note.image.name, f'map_data_points/{note.id}/image.png')

    def test_save_anonymous_map_data_point(self):
        # Given that no user is signed in
        # When requesting to save an Map Data Point over ReST
        url = reverse('mapdatapoint-list')
        fields = {
            'lat': '60.16134701761975',
            'lon': '24.944593941327188',
            'comment': 'Nice view',
            'tags': ['Entrance', 'Steps']
        }
        response = self.client.post(url, data=fields, format='json')

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # And a note is created in db:
        note = models.MapDataPoint.objects.get()

        # And it registers no user as the creator of the note:
        self.assertEqual(note.created_by_id, None)
        self.assertEqual(note.modified_by_id, None)

        # And it creates any passed tags:
        self.assertSetEqual(set(note.tags), set(fields['tags']))

        # And when subsequently requesting to attach an image to the note
        with open(os.path.join(os.path.dirname(__file__), 'test_image.png'), 'rb') as file:
            file_content = file.read()
        uploaded_file = SimpleUploadedFile("image.png", file_content, content_type="image/png")
        url = reverse('mapdatapoint-detail', kwargs={'pk': note.id})
        response = self.client.patch(url, data={'image': uploaded_file}, format='multipart')

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And a note is updated in db:
        note = models.MapDataPoint.objects.get()
        self.assertEqual(note.image.name, f'map_data_points/{note.id}/image.png')

    def test_save_anonymous_map_data_point_with_button_position(self):
        # Given that no user is signed in
        # And given a published Tag with button position field defined
        models.Tag.objects.create(tag='Smelly', button_position=1, published=timezone.now())

        # When requesting to save an Map Data Point over ReST, giving a button position
        url = reverse('mapdatapoint-list')
        fields = {
            'lat': '60.16134701761975',
            'lon': '24.944593941327188',
            'device_id': 'dev_1234',
            'button_position': 1
        }
        response = self.client.post(url, data=fields, format='json')

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # And a note is created in db:
        note = models.MapDataPoint.objects.get()

        # And it creates tags based on given button position:
        self.assertSetEqual(set(note.tags), set(['Smelly']))
        self.assertEqual(note.device_id, 'dev_1234')

    def test_update_map_data_point_tags(self):
        # Given that a user is signed in
        user = self.create_and_login_user()

        # And given a successfully created Map Data Point
        note = models.MapDataPoint.objects.create(lat='60.16134701761975', lon='24.944593941327188',
                                                  created_by=user)

        # When requesting to update an Map Data Point over ReST, giving a list of tags to add
        url = reverse('mapdatapoint-detail', kwargs={'pk': note.id})
        fields = {'tags': ['Entrance', 'Steps']}
        response = self.client.patch(url, data=fields, format='json')

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And the passed tags are created:
        note = models.MapDataPoint.objects.get()
        self.assertSetEqual(set(note.tags), set(fields['tags']))

        # And when subsequently requesting to update the note, giving another list of tags
        fields = {'tags': ['Entrance']}
        response = self.client.patch(url, data=fields, format='json')

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And the tags have been changed:
        note = models.MapDataPoint.objects.get()
        self.assertSetEqual(set(note.tags), set(fields['tags']))

    def test_review_features(self):
        # Given that a reviewer user is signed in
        user = self.create_and_login_reviewer()

        # And given a successfully created Map Data Point
        note = models.MapDataPoint.objects.create(lat='60.16134701761975', lon='24.944593941327188')

        # When requesting to mark the Map Data Point as processed over ReST
        url = reverse('mapdatapoint-mark-processed', kwargs={'pk': note.id})
        response = self.client.put(url)

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And the note is updated in db:
        note = models.MapDataPoint.objects.get()
        self.assertEqual(note.processed_by_id, user.id)

    def test_hide_features(self):
        # Given that a reviewer user is signed in
        user = self.create_and_login_reviewer()

        # And given a successfully created Map Data Point
        note = models.MapDataPoint.objects.create(lat='60.16134701761975', lon='24.944593941327188')

        # When requesting to mark the Map Data Point as hidden over ReST
        url = reverse('mapdatapoint-hide-note', kwargs={'pk': note.id})
        response = self.client.put(url, data={'hidden_reason': 'Too ugly.'})

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And a note is updated in db:
        note = models.MapDataPoint.objects.get()
        self.assertEqual(note.processed_by_id, user.id)
        self.assertEqual(note.hidden_reason, 'Too ugly.')

        # And the note is not shown in further requests to list Map Data Points
        url = reverse('mapdatapoint-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_vote_on_map_data_point(self):
        # Given that a user is signed in
        user = self.create_and_login_user()

        # And given a successfully created Map Data Point
        note = models.MapDataPoint.objects.create(lat='60.16134701761975', lon='24.944593941327188')

        # When requesting to upvote the Map Data Point over ReST
        url = reverse('mapdatapoint-upvote', kwargs={'pk': note.id})
        response = self.client.put(url)

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And the upvote is created:
        note = models.MapDataPoint.objects.get()
        #  self.assertSetEqual(set(response.json()['upvotes']), set([user.id]))
        self.assertSetEqual(set(note.upvotes.values_list('user_id', flat=True)), set([user.id]))

        # And when subsequently requesting to downvote the note
        url = reverse('mapdatapoint-downvote', kwargs={'pk': note.id})
        response = self.client.put(url)

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And the votes have been changed:
        note = models.MapDataPoint.objects.get()
        self.assertSetEqual(set(note.upvotes.values_list('user_id', flat=True)), set())
        #  self.assertSetEqual(set(response.json()['downvotes']), set([user.id]))
        self.assertSetEqual(set(note.downvotes.values_list('user_id', flat=True)), set([user.id]))

    def test_comment_on_map_data_point(self):
        # Given that a user is signed in
        user = self.create_and_login_user()

        # And given a successfully created Map Data Point
        user2 = User.objects.create(username='other_user')
        note = models.MapDataPoint.objects.create(lat='60.16134701761975', lon='24.944593941327188', created_by=user2)

        # When requesting to comment the Map Data Point over ReST
        url = reverse('mapdatapointcomment-list')
        response = self.client.post(url, {'map_data_point': note.id, 'comment': 'nice!'})

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # And the comment is created:
        note = models.MapDataPoint.objects.get()
        self.assertSetEqual(set(note.comments.values_list('comment', flat=True)), set(['nice!']))

        # And it is included with the note when fetched over ReST
        url = reverse('mapdatapoint-detail', kwargs={'pk': note.id})
        response = self.client.get(url)
        self.assertEqual(response.json()['comments'][0]['comment'], 'nice!')

        # And a notification of the comment is created for the note creator:
        self.assertEqual(user2.notifications.count(), 1)

        # And when subsequently requesting to delete the note
        url = reverse('mapdatapointcomment-detail', kwargs={'pk': note.comments.first().id})
        response = self.client.delete(url)

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # And the comment is deleted:
        note = models.MapDataPoint.objects.get()
        self.assertSetEqual(set(note.comments.values_list('comment', flat=True)), set([]))

    def test_map_data_points_as_geojson(self):
        # Given that there are some Map Data Points in the db
        note = models.MapDataPoint.objects.create(**{
            'lat': '60.16134701761975',
            'lon': '24.944593941327188',
            'comment': 'Nice view'})

        # When requesting the notes as geojson
        url = reverse('map_data_points_geojson')
        response = self.client.get(url)

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And it contains the notes as geojson:
        props = response.json()['features'][0]['properties']
        self.assertDictEqual(response.json(), {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [24.94459394, 60.16134702]},
                'properties': {
                    'id': note.id,
                    'comment': 'Nice view',
                    'lat': '60.16134702',
                    'lon': '24.94459394',
                    'is_processed': False,
                    'created_at': props['created_at'],
                    'modified_at': props['modified_at'],
                }
            }]
        })

    def test_rejected_map_data_points_not_in_geojson(self):
        # And given that there are some Map Data Points in the db marked as not visible
        note = models.MapDataPoint.objects.create(**{
            'lat': '60.16134701761975',
            'lon': '24.944593941327188',
            'comment': 'Nice view',
            'visible': False})

        # When requesting the notes as geojson
        url = reverse('map_data_points_geojson')
        response = self.client.get(url)

        # Then an OK response is received:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # And it does not contain the invisible notes:
        self.assertDictEqual(response.json(), {
            'type': 'FeatureCollection',
            'features': []
        })
