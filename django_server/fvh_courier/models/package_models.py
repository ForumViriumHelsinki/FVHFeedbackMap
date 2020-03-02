import uuid as uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from twilio.rest import Client

from .base import BaseLocation, TimestampedModel


class Address(BaseLocation):
    street_address = models.CharField(verbose_name=_('street address'), max_length=128)
    postal_code = models.CharField(verbose_name=_('postal code'), max_length=16)
    city = models.CharField(verbose_name=_('city'), max_length=64)
    country = models.CharField(verbose_name=_('country'), max_length=64)

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    def __str__(self):
        return self.street_address


class Package(TimestampedModel):
    pickup_at = models.ForeignKey(Address, verbose_name=_('pickup location'), related_name='outbound_packages',
                                  on_delete=models.PROTECT)
    deliver_to = models.ForeignKey(Address, verbose_name=_('destination'), related_name='inbound_packages',
                                   on_delete=models.PROTECT)

    height = models.PositiveIntegerField(verbose_name=_('height'), help_text=_('in cm'))
    width = models.PositiveIntegerField(verbose_name=_('width'), help_text=_('in cm'))
    depth = models.PositiveIntegerField(verbose_name=_('depth'), help_text=_('in cm'))

    weight = models.DecimalField(verbose_name=_('weight'), help_text=_('in kg'), max_digits=7, decimal_places=2)

    sender = models.ForeignKey(User, verbose_name=_('sender'), related_name='sent_packages', on_delete=models.PROTECT)

    recipient = models.CharField(max_length=128, verbose_name=_('recipient'))
    recipient_phone = models.CharField(max_length=32, verbose_name=_('recipient phone number'))

    courier = models.ForeignKey(User, verbose_name=_('courier'), null=True, blank=True,
                                related_name='delivered_packages', on_delete=models.PROTECT)

    earliest_pickup_time = models.DateTimeField(verbose_name=_('earliest pickup time'))
    latest_pickup_time = models.DateTimeField(verbose_name=_('latest pickup time'))

    earliest_delivery_time = models.DateTimeField(verbose_name=_('earliest delivery time'))
    latest_delivery_time = models.DateTimeField(verbose_name=_('latest delivery time'))

    picked_up_time = models.DateTimeField(verbose_name=_('picked up at'), blank=True, null=True)
    delivered_time = models.DateTimeField(verbose_name=_('delivered at'), blank=True, null=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _('package')
        verbose_name_plural = _('packages')
        ordering = ['-earliest_pickup_time']

    @classmethod
    def available_packages(cls):
        """
        Return all packages for which delivery has been requested but which are not yet reserved by any courier.
        """
        return cls.objects.filter(courier__isnull=True)


class PackageSMS(TimestampedModel):
    message_types = [{
        'name': 'reservation',
        'template': 'Your package to {recipient} was reserved by {courier}. See delivery progress: {url}'
    }, {
        'name': 'pickup',
        'template': 'Your package from {sender} was picked up for delivery. See delivery progress: {url}'
    }, {
        'name': 'delivery',
        'template': 'Your package to {recipient} has been delivered.'
    }]

    types_by_name = dict((t['name'], i) for i, t in enumerate(message_types))
    templates_by_name = dict((t['name'], t['template']) for t in message_types)

    message_type = models.PositiveSmallIntegerField(choices=((i, t['name']) for i, t in enumerate(message_types)))
    recipient_number = models.CharField(max_length=32)
    twilio_sid = models.CharField(max_length=64)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='sms_messages')
    content = models.TextField()

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def render_message(cls, message_type, package, referer):
        return cls.templates_by_name[message_type].format(
            recipient=package.recipient,
            sender=package.sender.get_full_name(),
            courier=package.courier.get_full_name(),
            url='{}#/package/{}'.format(referer or settings.FRONTEND_ROOT, package.uuid))

    @classmethod
    def send_message(cls, package, message_type, to_number, referer):
        message = cls(
            package=package,
            message_type=cls.types_by_name[message_type],
            recipient_number=to_number,
            content=cls.render_message(message_type, package, referer))
        client = cls.get_twilio_client()
        if client:
            twilio_msg = client.messages.create(
                body=message.content,
                to=to_number,
                from_=settings.TWILIO['SENDER_NR'])
            message.twilio_sid = twilio_msg.sid
        message.save()

    @classmethod
    def message_sender(cls, package, message_type, referer):
        sender_phones = package.sender.phone_numbers.all()
        if not len(sender_phones):
            return
        cls.send_message(package, message_type, sender_phones[0].number, referer)

    @classmethod
    def notify_sender_of_reservation(cls, package, referer):
        cls.message_sender(package, 'reservation', referer)

    @classmethod
    def notify_recipient_of_pickup(cls, package, referer):
        cls.send_message(package, 'pickup', package.recipient_phone, referer)

    @classmethod
    def notify_sender_of_delivery(cls, package, referer):
        cls.message_sender(package, 'delivery', referer)

    @classmethod
    def get_twilio_client(cls):
        if settings.TWILIO['ACCOUNT_SID'] != 'configure in local settings':
            return Client(settings.TWILIO['ACCOUNT_SID'], settings.TWILIO['AUTH_TOKEN'])