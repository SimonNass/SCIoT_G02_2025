from __future__ import annotations
import os
from typing import Any
import httpx
from dotenv import load_dotenv
import random


load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:81").rstrip("/")
API_KEY     = os.getenv("API_KEY",     "changeme")

class Backend:
    def __init__(self) -> None:
        self.cli = httpx.AsyncClient(
            base_url=BACKEND_URL,
            headers={"X-API-Key": API_KEY},
            timeout=10,
        )

    async def _get (self, p:str)                -> Any:  r = await self.cli.get (p); r.raise_for_status(); return r.json()
    async def _post(self, p:str, payload:dict)  -> Any:  r = await self.cli.post(p, json=payload); (r.raise_for_status() if r.status_code!=409 else None); return r.json()
    async def _delete(self, p:str) -> Any:
            r = await self.cli.delete(p)
            r.raise_for_status()
            return r.json()

    async def list_floors(self):           return (await self._get("/floors/list"))["floors"]
    async def list_rooms (self, floor:int): return (await self._get(f"/floors/{floor}/rooms/list"))["rooms"]
    async def list_devices(self, floor:int, room:str): return (await self._get(f"/floors/{floor}/rooms/{room}/devices/list"))["devices"]

    async def list_all_rooms(self)->list[dict]:
        data = await self.list_floors()
        flat=[]
        for f in data:
            for r in f["rooms"]:
                r=r.copy(); r.setdefault("created_at",None); r.setdefault("last_cleaned",None)
                r["floor_number"]=f["floor_number"]; r["floor_name"]=f["floor_name"]
                flat.append(r)
        return flat

    # demo data
    async def seed_if_needed(self)->None:
        # await self.clear_database()
        if await self.list_floors(): return
        meta=[(1,"Ground","Lobby / conf.",8),
              (2,"North","Std queen rooms",10),
              (3,"South","Deluxe / suite",6),
              (4,"Exec","Suites & lounge",8)]
        for n,name,desc,_ in meta:
            await self._post("/floors/create",{"floor_number":n,"floor_name":name,"description":desc,"rooms":[]})
        for n,_,_,cnt in meta:
            batch=[]
            for i in range(1,cnt+1):
                rn=f"{n}{i:02d}"
                if i%5==0: typ,cap="Suite",4
                elif i%3==0: typ,cap="Deluxe",3
                else: typ,cap="Standard",1 if random.random()<.3 else 2
                batch.append({"room_number":rn,"room_type":typ,"capacity":cap})

            await self._post(f"/floors/{n}/rooms/create",{"rooms":batch})

    async def set_room_occupancy(self, floor_number: int, room_number: str, is_occupied: bool):
        """Sets the occupancy status for a specific room."""
        return await self._post(f"/floors/{floor_number}/rooms/{room_number}/occupancy/set", {"is_occupied": is_occupied})

    async def set_actuator_value(self, device_id: str, new_value: Any):
        """Sets the value for a specific actuator."""
        return await self._post(f"/devices/{device_id}/set", {"new_value": new_value})

    async def set_sensor_value(self, device_id: str, new_value: Any):
        """Sets the value for a specific sensor."""
        return await self._post(f"/devices/sensor/{device_id}/set", {"new_value": new_value})

    async def get_sensor_data_interval(self, device_id: str, interval: int):
        """Gets sensor data with interval sampling."""
        return await self._post(f"/devices/{device_id}/sensor_data", {"interval": interval})

    async def get_recent_sensor_data(self, device_id: str, minutes: int, interval: int):
        """Gets recent sensor data from the last n minutes with interval sampling."""
        return await self._post(f"/devices/{device_id}/sensor_data/recent", {"minutes": minutes, "interval": interval})
    async def get_mapping_matrices(self):
        """Gets the actuator-sensor mapping matrices."""
        return await self._get("/api/mappings/matrices")

    async def set_device_offline(self, device_id: str):
        """Sets a specific device to offline status."""
        return await self._post(f"/devices/{device_id}/offline/set", {})

    async def set_bulk_devices_offline(self, minutes: int):
        """Sets all devices not seen for a given number of minutes to offline."""
        return await self._post("/devices/bulk/offline/set", {"minutes": minutes})

    async def delete_device(self, device_id: str):
        """Deletes a specific device."""
        return await self._delete(f"/devices/{device_id}/delete")

    async def list_type_name_configs(self):
        """Gets all type name configurations."""
        return (await self._get("/type_name_configs/list"))["configs"]

    async def set_type_name_config(self, device_type: str, type_name: str, lower_mid_limit: float, upper_mid_limit: float):
        """Sets the threshold values for a specific type name config."""
        payload = {
            "device_type": device_type,
            "type_name": type_name,
            "lower_mid_limit": lower_mid_limit,
            "upper_mid_limit": upper_mid_limit
        }
        return await self._post("/type_name_configs/set", payload)

    async def clear_database(self):
        return await self._delete("/cleardb")

    # PDDL plans retrieval

    async def list_all_plans(self) -> dict:
        """GET /api/planning/plans/list → {'plans': [...], 'total_plans': N}"""
        return await self._get('/api/planning/plans/list')

    async def list_plans_for_floor(self, floor_number: int) -> dict:
        """GET /api/planning/floors/{floor_number}/plans/list"""
        return await self._get(f'/api/planning/floors/{floor_number}/plans/list')

    async def list_plans_for_room(self, room_number: str) -> dict:
        """GET /api/planning/rooms/{room_number}/plans/list"""
        return await self._get(f'/api/planning/rooms/{room_number}/plans/list')

    async def get_latest_plan(self) -> dict:
        """GET /api/planning/plans/latest → most recent plan object"""
        return await self._get('/api/planning/plans/latest')

    async def get_latest_plan_for_floor(self, floor_number: int) -> dict:
        """GET /api/planning/floors/{floor_number}/plans/latest"""
        return await self._get(f'/api/planning/floors/{floor_number}/plans/latest')

    async def get_latest_plan_for_room(self, room_number: str) -> dict:
        """GET /api/planning/rooms/{room_number}/plans/latest"""
        return await self._get(f'/api/planning/rooms/{room_number}/plans/latest')

    # Run planner on demand

    async def run_planner_all(self) -> dict:
        """GET /api/planning/run_planner → plan for entire building"""
        return await self._get('/api/planning/run_planner')

    async def run_planner_for_room(self, room_number: str) -> dict:
        """GET /api/planning/run_planner/room/{room_number}"""
        return await self._get(f'/api/planning/run_planner/room/{room_number}')

    async def run_planner_for_room(self, room_number: str) -> dict:
        """GET /api/planning/run_planner/room/{room_number}"""
        return await self._get(f'/api/planning/run_planner/room/{room_number}')