# -*- coding: utf-8 -*-
"""
LINE Messaging Templates - Flex Message builders for various notifications
"""
import logging

_logger = logging.getLogger(__name__)


class LineMessageBuilder:
    """
    Builder for LINE message objects
    Supports Text, Flex (Bubble, Carousel), Quick Reply
    """

    @staticmethod
    def text(text):
        """Simple text message"""
        return {
            'type': 'text',
            'text': text,
        }

    @staticmethod
    def sticker(package_id, sticker_id):
        """Sticker message"""
        return {
            'type': 'sticker',
            'packageId': str(package_id),
            'stickerId': str(sticker_id),
        }

    @staticmethod
    def image(original_url, preview_url=None):
        """Image message"""
        return {
            'type': 'image',
            'originalContentUrl': original_url,
            'previewImageUrl': preview_url or original_url,
        }

    @staticmethod
    def quick_reply(items):
        """
        Quick reply buttons

        Args:
            items: List of quick reply items
                   Each item: {'type': 'action', 'action': {...}}
        """
        return {
            'items': items,
        }

    @staticmethod
    def quick_reply_action(label, data, display_text=None):
        """Create a postback quick reply action"""
        return {
            'type': 'action',
            'action': {
                'type': 'postback',
                'label': label,
                'data': data,
                'displayText': display_text or label,
            }
        }

    @staticmethod
    def quick_reply_message(label, text):
        """Create a message quick reply action"""
        return {
            'type': 'action',
            'action': {
                'type': 'message',
                'label': label,
                'text': text,
            }
        }


class FlexMessageBuilder:
    """
    Builder for LINE Flex Messages
    """

    @staticmethod
    def bubble(header=None, hero=None, body=None, footer=None, styles=None):
        """
        Create a Flex Bubble container

        Args:
            header: Header box component
            hero: Hero image component
            body: Body box component
            footer: Footer box component
            styles: Bubble styles
        """
        bubble = {
            'type': 'bubble',
        }

        if header:
            bubble['header'] = header
        if hero:
            bubble['hero'] = hero
        if body:
            bubble['body'] = body
        if footer:
            bubble['footer'] = footer
        if styles:
            bubble['styles'] = styles

        return bubble

    @staticmethod
    def carousel(bubbles):
        """
        Create a Flex Carousel container

        Args:
            bubbles: List of bubble containers (max 12)
        """
        return {
            'type': 'carousel',
            'contents': bubbles[:12],
        }

    @staticmethod
    def flex_message(alt_text, contents):
        """
        Wrap Flex content in a message object

        Args:
            alt_text: Alternative text for notifications
            contents: Bubble or Carousel container
        """
        return {
            'type': 'flex',
            'altText': alt_text,
            'contents': contents,
        }

    # ==================== Component Builders ====================

    @staticmethod
    def box(layout, contents, **kwargs):
        """
        Create a box component

        Args:
            layout: 'horizontal', 'vertical', 'baseline'
            contents: List of components
            **kwargs: Additional properties (spacing, margin, etc.)
        """
        component = {
            'type': 'box',
            'layout': layout,
            'contents': contents,
        }
        component.update(kwargs)
        return component

    @staticmethod
    def text_component(text, **kwargs):
        """
        Create a text component

        Args:
            text: Text content
            **kwargs: size, weight, color, wrap, align, etc.
        """
        component = {
            'type': 'text',
            'text': str(text),
        }
        component.update(kwargs)
        return component

    @staticmethod
    def image_component(url, **kwargs):
        """
        Create an image component

        Args:
            url: Image URL
            **kwargs: size, aspectRatio, aspectMode, etc.
        """
        component = {
            'type': 'image',
            'url': url,
        }
        component.update(kwargs)
        return component

    @staticmethod
    def button(action, **kwargs):
        """
        Create a button component

        Args:
            action: Action object
            **kwargs: style, height, color, etc.
        """
        component = {
            'type': 'button',
            'action': action,
        }
        component.update(kwargs)
        return component

    @staticmethod
    def separator(**kwargs):
        """Create a separator component"""
        component = {'type': 'separator'}
        component.update(kwargs)
        return component

    @staticmethod
    def spacer(**kwargs):
        """Create a spacer component"""
        component = {'type': 'spacer'}
        component.update(kwargs)
        return component

    @staticmethod
    def filler():
        """Create a filler component"""
        return {'type': 'filler'}

    # ==================== Action Builders ====================

    @staticmethod
    def uri_action(label, uri):
        """Create a URI action"""
        return {
            'type': 'uri',
            'label': label,
            'uri': uri,
        }

    @staticmethod
    def postback_action(label, data, display_text=None):
        """Create a postback action"""
        action = {
            'type': 'postback',
            'label': label,
            'data': data,
        }
        if display_text:
            action['displayText'] = display_text
        return action

    @staticmethod
    def message_action(label, text):
        """Create a message action"""
        return {
            'type': 'message',
            'label': label,
            'text': text,
        }


class OrderNotificationTemplates:
    """
    Pre-built Flex Message templates for order notifications
    """

    @staticmethod
    def order_confirmation(order_data, liff_url=None):
        """
        Create order confirmation Flex Message

        Args:
            order_data: Dict with order info
                {order_name, date, customer, lines, subtotal, tax, total, currency}
            liff_url: LIFF URL for viewing order details
        """
        # Build order lines
        line_components = []
        for line in order_data.get('lines', [])[:5]:  # Max 5 items shown
            line_components.append(
                FlexMessageBuilder.box('horizontal', [
                    FlexMessageBuilder.text_component(
                        line['product_name'][:20],
                        size='sm',
                        color='#555555',
                        flex=0
                    ),
                    FlexMessageBuilder.text_component(
                        f"x{int(line['quantity'])}",
                        size='sm',
                        color='#111111',
                        align='end'
                    ),
                ])
            )

        if len(order_data.get('lines', [])) > 5:
            line_components.append(
                FlexMessageBuilder.text_component(
                    f"... and {len(order_data['lines']) - 5} more items",
                    size='xs',
                    color='#aaaaaa',
                    margin='md'
                )
            )

        currency = order_data.get('currency', '฿')

        # Body
        body = FlexMessageBuilder.box('vertical', [
            # Title
            FlexMessageBuilder.text_component(
                'Order Confirmed',
                weight='bold',
                color='#1DB446',
                size='sm'
            ),
            # Order number
            FlexMessageBuilder.text_component(
                order_data.get('order_name', 'Order'),
                weight='bold',
                size='xxl',
                margin='md'
            ),
            # Date
            FlexMessageBuilder.text_component(
                order_data.get('date', ''),
                size='xs',
                color='#aaaaaa',
                wrap=True
            ),
            FlexMessageBuilder.separator(margin='xxl'),
            # Order items
            FlexMessageBuilder.box('vertical', line_components, margin='xxl', spacing='sm'),
            FlexMessageBuilder.separator(margin='xxl'),
            # Total
            FlexMessageBuilder.box('horizontal', [
                FlexMessageBuilder.text_component('Total', size='sm', color='#555555'),
                FlexMessageBuilder.text_component(
                    f"{currency}{order_data.get('total', 0):,.2f}",
                    size='lg',
                    color='#111111',
                    weight='bold',
                    align='end'
                ),
            ], margin='xxl'),
        ])

        # Footer
        footer_contents = []
        if liff_url:
            footer_contents.append(
                FlexMessageBuilder.button(
                    FlexMessageBuilder.uri_action('View Order', liff_url),
                    style='primary',
                    color='#1DB446'
                )
            )

        footer = FlexMessageBuilder.box('vertical', footer_contents, spacing='sm') if footer_contents else None

        bubble = FlexMessageBuilder.bubble(body=body, footer=footer)

        return FlexMessageBuilder.flex_message(
            f"Order {order_data.get('order_name', '')} confirmed",
            bubble
        )

    @staticmethod
    def shipping_notification(order_data, tracking_number=None, tracking_url=None):
        """
        Create shipping notification Flex Message

        Args:
            order_data: Dict with order info
            tracking_number: Tracking number
            tracking_url: URL to track shipment
        """
        body_contents = [
            FlexMessageBuilder.text_component(
                'Shipped!',
                weight='bold',
                color='#1DB446',
                size='sm'
            ),
            FlexMessageBuilder.text_component(
                order_data.get('order_name', 'Your order'),
                weight='bold',
                size='xl',
                margin='md'
            ),
            FlexMessageBuilder.text_component(
                'Your order is on the way!',
                size='sm',
                color='#aaaaaa',
                wrap=True,
                margin='md'
            ),
        ]

        if tracking_number:
            body_contents.extend([
                FlexMessageBuilder.separator(margin='xxl'),
                FlexMessageBuilder.box('horizontal', [
                    FlexMessageBuilder.text_component('Tracking', size='sm', color='#aaaaaa'),
                    FlexMessageBuilder.text_component(
                        tracking_number,
                        size='sm',
                        color='#111111',
                        weight='bold',
                        align='end'
                    ),
                ], margin='xxl'),
            ])

        body = FlexMessageBuilder.box('vertical', body_contents)

        # Footer with tracking button
        footer_contents = []
        if tracking_url:
            footer_contents.append(
                FlexMessageBuilder.button(
                    FlexMessageBuilder.uri_action('Track Shipment', tracking_url),
                    style='primary',
                    color='#1DB446'
                )
            )

        footer = FlexMessageBuilder.box('vertical', footer_contents, spacing='sm') if footer_contents else None

        bubble = FlexMessageBuilder.bubble(body=body, footer=footer)

        return FlexMessageBuilder.flex_message(
            f"Order {order_data.get('order_name', '')} has been shipped!",
            bubble
        )

    @staticmethod
    def welcome_message(channel_name, liff_url=None):
        """
        Create welcome message for new followers

        Args:
            channel_name: Name of the LINE channel/shop
            liff_url: LIFF URL to start shopping
        """
        body = FlexMessageBuilder.box('vertical', [
            FlexMessageBuilder.text_component(
                f'Welcome to {channel_name}!',
                weight='bold',
                size='xl',
                align='center'
            ),
            FlexMessageBuilder.text_component(
                'Thank you for following us. Start shopping now!',
                size='sm',
                color='#aaaaaa',
                wrap=True,
                align='center',
                margin='md'
            ),
        ])

        footer_contents = []
        if liff_url:
            footer_contents.append(
                FlexMessageBuilder.button(
                    FlexMessageBuilder.uri_action('Start Shopping', liff_url),
                    style='primary',
                    color='#00B900'
                )
            )

        footer = FlexMessageBuilder.box('vertical', footer_contents) if footer_contents else None

        bubble = FlexMessageBuilder.bubble(body=body, footer=footer)

        return FlexMessageBuilder.flex_message(
            f'Welcome to {channel_name}!',
            bubble
        )

    @staticmethod
    def product_carousel(products, base_url):
        """
        Create product carousel Flex Message

        Args:
            products: List of product dicts
                {id, name, price, currency, image_url, description}
            base_url: Base URL for LIFF/product links
        """
        bubbles = []

        for product in products[:10]:  # Max 10 products
            hero = FlexMessageBuilder.image_component(
                product.get('image_url', f'{base_url}/web/static/img/placeholder.png'),
                size='full',
                aspectRatio='4:3',
                aspectMode='cover'
            )

            body = FlexMessageBuilder.box('vertical', [
                FlexMessageBuilder.text_component(
                    product.get('name', 'Product'),
                    weight='bold',
                    size='md',
                    wrap=True
                ),
                FlexMessageBuilder.text_component(
                    f"{product.get('currency', '฿')}{product.get('price', 0):,.2f}",
                    size='lg',
                    color='#1DB446',
                    weight='bold',
                    margin='md'
                ),
            ])

            footer = FlexMessageBuilder.box('vertical', [
                FlexMessageBuilder.button(
                    FlexMessageBuilder.uri_action(
                        'View',
                        f"{base_url}/line-buyer/product/{product.get('id')}"
                    ),
                    style='primary'
                ),
                FlexMessageBuilder.button(
                    FlexMessageBuilder.postback_action(
                        'Add to Cart',
                        f"action=add_to_cart&product_id={product.get('id')}"
                    ),
                    style='secondary',
                    margin='sm'
                ),
            ], spacing='sm')

            bubbles.append(
                FlexMessageBuilder.bubble(hero=hero, body=body, footer=footer)
            )

        carousel = FlexMessageBuilder.carousel(bubbles)

        return FlexMessageBuilder.flex_message('Check out these products!', carousel)
