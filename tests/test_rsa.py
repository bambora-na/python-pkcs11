"""
PKCS#11 Public Key Cryptography

These tests assume SoftHSMv2 with a single token initialized called DEMO.
"""

from pkcs11 import Attribute, KeyType, ObjectClass

from . import TestCase


class PKCS11PKCTests(TestCase):

    def setUp(self):
        super().setUp()
        self.public, self.private = self.session.generate_keypair(KeyType.RSA,
                                                                  1024,
                                                                  store=False)

    def test_rsa_sign(self):
        data = b'HELLO WORLD' * 1024

        signature = self.private.sign(data)
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertTrue(self.public.verify(data, signature))
        self.assertFalse(self.public.verify(data, b'1234'))

    def test_rsa_sign_stream(self):
        data = (
            b'I' * 16,
            b'N' * 16,
            b'P' * 16,
            b'U' * 16,
            b'T' * 10,  # don't align to the blocksize
        )

        signature = self.private.sign(data)
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)
        self.assertTrue(self.public.verify(data, signature))

    def test_key_wrap(self):
        key = self.session.generate_key(KeyType.AES, 128,
                                        store=False,
                                        template={
                                            Attribute.EXTRACTABLE: True,
                                            Attribute.SENSITIVE: False,
                                        })

        data = self.public.wrap_key(key)
        self.assertNotEqual(data, key[Attribute.VALUE])

        key2 = self.private.unwrap_key(ObjectClass.SECRET_KEY,
                                       KeyType.AES,
                                       data,
                                       store=False,
                                       template={
                                               Attribute.EXTRACTABLE: True,
                                               Attribute.SENSITIVE: False,
                                       })

        self.assertEqual(key[Attribute.VALUE], key2[Attribute.VALUE])