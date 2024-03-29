# -*- coding: utf-8 -*-
#
# Copyright (c) ZeroC, Inc. All rights reserved.
#
#
# Ice version 3.7.9
#
# <auto-generated>
#
# Generated from file `RealEstate.ice'
#
# Warning: do not edit this file.
#
# </auto-generated>
#

from sys import version_info as _version_info_
import Ice, IcePy

# Start of module RealEstate
_M_RealEstate = Ice.openModule('RealEstate')
__name__ = 'RealEstate'

if 'GenericError' not in _M_RealEstate.__dict__:
    _M_RealEstate.GenericError = Ice.createTempClass()
    class GenericError(Ice.UserException):
        def __init__(self, reason=''):
            self.reason = reason

        def __str__(self):
            return IcePy.stringifyException(self)

        __repr__ = __str__

        _ice_id = '::RealEstate::GenericError'

    _M_RealEstate._t_GenericError = IcePy.defineException('::RealEstate::GenericError', GenericError, (), False, None, (('reason', (), IcePy._t_string, False, 0),))
    GenericError._ice_type = _M_RealEstate._t_GenericError

    _M_RealEstate.GenericError = GenericError
    del GenericError

_M_RealEstate._t_RealEstateInterface = IcePy.defineValue('::RealEstate::RealEstateInterface', Ice.Value, -1, (), False, True, None, ())

if 'RealEstateInterfacePrx' not in _M_RealEstate.__dict__:
    _M_RealEstate.RealEstateInterfacePrx = Ice.createTempClass()
    class RealEstateInterfacePrx(Ice.ObjectPrx):

        def getZoneData(self, context=None):
            return _M_RealEstate.RealEstateInterface._op_getZoneData.invoke(self, ((), context))

        def getZoneDataAsync(self, context=None):
            return _M_RealEstate.RealEstateInterface._op_getZoneData.invokeAsync(self, ((), context))

        def begin_getZoneData(self, _response=None, _ex=None, _sent=None, context=None):
            return _M_RealEstate.RealEstateInterface._op_getZoneData.begin(self, ((), _response, _ex, _sent, context))

        def end_getZoneData(self, _r):
            return _M_RealEstate.RealEstateInterface._op_getZoneData.end(self, _r)

        def getPropertyData(self, context=None):
            return _M_RealEstate.RealEstateInterface._op_getPropertyData.invoke(self, ((), context))

        def getPropertyDataAsync(self, context=None):
            return _M_RealEstate.RealEstateInterface._op_getPropertyData.invokeAsync(self, ((), context))

        def begin_getPropertyData(self, _response=None, _ex=None, _sent=None, context=None):
            return _M_RealEstate.RealEstateInterface._op_getPropertyData.begin(self, ((), _response, _ex, _sent, context))

        def end_getPropertyData(self, _r):
            return _M_RealEstate.RealEstateInterface._op_getPropertyData.end(self, _r)

        @staticmethod
        def checkedCast(proxy, facetOrContext=None, context=None):
            return _M_RealEstate.RealEstateInterfacePrx.ice_checkedCast(proxy, '::RealEstate::RealEstateInterface', facetOrContext, context)

        @staticmethod
        def uncheckedCast(proxy, facet=None):
            return _M_RealEstate.RealEstateInterfacePrx.ice_uncheckedCast(proxy, facet)

        @staticmethod
        def ice_staticId():
            return '::RealEstate::RealEstateInterface'
    _M_RealEstate._t_RealEstateInterfacePrx = IcePy.defineProxy('::RealEstate::RealEstateInterface', RealEstateInterfacePrx)

    _M_RealEstate.RealEstateInterfacePrx = RealEstateInterfacePrx
    del RealEstateInterfacePrx

    _M_RealEstate.RealEstateInterface = Ice.createTempClass()
    class RealEstateInterface(Ice.Object):

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::RealEstate::RealEstateInterface')

        def ice_id(self, current=None):
            return '::RealEstate::RealEstateInterface'

        @staticmethod
        def ice_staticId():
            return '::RealEstate::RealEstateInterface'

        def getZoneData(self, current=None):
            raise NotImplementedError("servant method 'getZoneData' not implemented")

        def getPropertyData(self, current=None):
            raise NotImplementedError("servant method 'getPropertyData' not implemented")

        def __str__(self):
            return IcePy.stringify(self, _M_RealEstate._t_RealEstateInterfaceDisp)

        __repr__ = __str__

    _M_RealEstate._t_RealEstateInterfaceDisp = IcePy.defineClass('::RealEstate::RealEstateInterface', RealEstateInterface, (), None, ())
    RealEstateInterface._ice_type = _M_RealEstate._t_RealEstateInterfaceDisp

    RealEstateInterface._op_getZoneData = IcePy.Operation('getZoneData', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (), (), ((), IcePy._t_string, False, 0), ())
    RealEstateInterface._op_getPropertyData = IcePy.Operation('getPropertyData', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (), (), ((), IcePy._t_string, False, 0), ())

    _M_RealEstate.RealEstateInterface = RealEstateInterface
    del RealEstateInterface

# End of module RealEstate
