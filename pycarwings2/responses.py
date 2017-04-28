# Copyright 2016 Jason Horne
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from datetime import date, timedelta, datetime
import pycarwings2

log = logging.getLogger(__name__)

def _time_remaining(t):
        minutes = float(0)
        if t:
                if ("hours" in t) and t["hours"]:
                        minutes = 60*float(t["hours"])
                elif ("HourRequiredToFull" in t) and t["HourRequiredToFull"]:
                        minutes = 60*float(t["HourRequiredToFull"])
                if ("minutes" in t) and t["minutes"]:
                        minutes += float(t["minutes"])
                elif ("MinutesRequiredToFull" in t) and t["MinutesRequiredToFull"]:
                        minutes += float(t["MinutesRequiredToFull"])

        return minutes


class CarwingsResponse:
        def __init__(self, response):
                op_result = None
                if ("operationResult" in response):
                        op_result = response["operationResult"]
                elif ("OperationResult" in response):
                        op_result = response["OperationResult"]

                # seems to indicate that the vehicle cannot be reached
                if ( "ELECTRIC_WAVE_ABNORMAL" == op_result):
                        log.error("could not establish communications with vehicle")
                        raise pycarwings2.CarwingsError("could not establish communications with vehicle")

        def _set_cruising_ranges(self, status, off_key="cruisingRangeAcOff", on_key="cruisingRangeAcOn"):
                self.cruising_range_ac_off_km = float(status[off_key]) / 1000
                self.cruising_range_ac_on_km = float(status[on_key]) / 1000

        def _set_timestamp(self, status):
                self.timestamp = datetime.strptime(status["timeStamp"], "%Y-%m-%d %H:%M:%S") # "2016-01-02 17:17:38"


class CarwingsInitialAppResponse(CarwingsResponse):
        def __init__(self, response):
                CarwingsResponse.__init__(self, response)
                self.baseprm = response["baseprm"]

"""
        example JSON response to login:

        {
                "status":200,
                "message":"success",
                "sessionId":"12345678-1234-1234-1234-1234567890",
                "VehicleInfoList": {
                        "VehicleInfo": [
                                {
                                        "charger20066":"false",
                                        "nickname":"LEAF",
                                        "telematicsEnabled":"true",
                                        "vin":"1ABCDEFG2HIJKLM3N"
                                }
                        ],
                        "vehicleInfo": [
                                {
                                        "charger20066":"false",
                                        "nickname":"LEAF",
                                        "telematicsEnabled":"true",
                                        "vin":"1ABCDEFG2HIJKLM3N"
                                }
                        ]
                },
                "vehicle": {
                        "profile": {
                                "vin":"1ABCDEFG2HIJKLM3N",
                                "gdcUserId":"FG12345678",
                                "gdcPassword":"password",
                                "encAuthToken":"ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                "dcmId":"123456789012",
                                "nickname":"Alpha124",
                                "status":"ACCEPTED",
                                "statusDate": "Aug 15, 2015 07:00 PM"
                        }
                },
                "EncAuthToken":"ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "CustomerInfo": {
                        "UserId":"AB12345678",
                        "Language":"en-US",
                        "Timezone":"America\/New_York",
                        "RegionCode":"NNA",
                        "OwnerId":"1234567890",
                        "Nickname":"Bravo456",
                        "Country":"US",
                        "VehicleImage":"\/content\/language\/default\/images\/img\/ph_car.jpg",
                        "UserVehicleBoundDurationSec":"999971200",
                        "VehicleInfo": {
                                "VIN":"1ABCDEFG2HIJKLM3N",
                                "DCMID":"201212345678",
                                "SIMID":"12345678901234567890",
                                "NAVIID":"1234567890",
                                "EncryptedNAVIID":"1234567890ABCDEFGHIJKLMNOP",
                                "MSN":"123456789012345",
                                "LastVehicleLoginTime":"",
                                "UserVehicleBoundTime":"2015-08-17T14:16:32Z",
                                "LastDCMUseTime":""
                        }
                },
                "UserInfoRevisionNo":"1"
        }
"""

class CarwingsLoginResponse(CarwingsResponse):
        def __init__(self, response):
                CarwingsResponse.__init__(self, response)
                self.answer = response # FUI EU!!

                profile = response["vehicle"]["profile"]
                self.gdc_user_id = profile["gdcUserId"]
                self.dcm_id = profile["dcmId"]
                self.vin = profile["vin"]

                # vehicleInfo block may be top level, or contained in a VehicleInfoList object;
                # why it's sometimes one way and sometimes another is not clear.
                if "VehicleInfoList" in response:
                        self.nickname = response["VehicleInfoList"]["vehicleInfo"][0]["nickname"]
                        self.custom_sessionid = response["VehicleInfoList"]["vehicleInfo"][0]["custom_sessionid"]
                elif "vehicleInfo" in response:
                        self.nickname = response["vehicleInfo"][0]["nickname"]
                        self.custom_sessionid = response["vehicleInfo"][0]["custom_sessionid"]

                customer_info = response["CustomerInfo"]
                self.tz = customer_info["Timezone"]
                self.language = customer_info["Language"]
                self.user_vehicle_bound_time = customer_info["VehicleInfo"]["UserVehicleBoundTime"]

                self.leafs = [ {
                        "vin": self.vin,
                        "nickname": self.nickname,
                        "bound_time": self.user_vehicle_bound_time
                } ]


class CarwingsBatteryStatusResponse(CarwingsResponse):
        def __init__(self, status):
                CarwingsResponse.__init__(self, status)
                self.answer = status

class CarwingsLatestClimateControlStatusResponse(CarwingsResponse):
        def __init__(self, status):
                CarwingsResponse.__init__(self, status)
                self.answer = status

class CarwingsStartClimateControlResponse(CarwingsResponse):
        def __init__(self, status):
                CarwingsResponse.__init__(self, status)
                self.answer = status

class CarwingsStopClimateControlResponse(CarwingsResponse):
        def __init__(self, status):
                CarwingsResponse.__init__(self, status)
                self.answer = status

class CarwingsClimateControlScheduleResponse(CarwingsResponse):
        def __init__(self, status):
                CarwingsResponse.__init__(self, status)
                self.answer = status

class CarwingsDrivingAnalysisResponse(CarwingsResponse):
        def __init__(self, status):
                CarwingsResponse.__init__(self, status)
                self.answer = status 

class CarwingsLatestBatteryStatusResponse(CarwingsResponse):
        def __init__(self, status):
                CarwingsResponse.__init__(self, status)
                self.answer = status

class CarwingsElectricRateSimulationResponse(CarwingsResponse):
        def __init__(self, status):
                CarwingsResponse.__init__(self, status)
                self.answer = status 
