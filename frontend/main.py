# nicegui_app.py – verified with NiceGUI 1.4.18
# ------------------------------------------------------------
# Run with:
#   pip install nicegui>=1.4 httpx pydantic python-dotenv
#   BACKEND_URL=http://localhost API_KEY=my_api_key python nicegui_app.py
# ------------------------------------------------------------
from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()
import httpx
from pydantic import BaseModel
from nicegui import ui

# ------------------------------------------------------------------
# 1. REST helper
# ------------------------------------------------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost").rstrip("/")
API_KEY     = os.getenv("API_KEY", "changeme")

class BackendClient:
    def __init__(self, base_url: str, api_key: str):
        self.cli = httpx.AsyncClient(base_url=base_url, headers={"X-API-Key": api_key}, timeout=10)

    async def _get(self, path: str):
        r = await self.cli.get(path)
        r.raise_for_status()
        data = r.json()
        ui.notify(f"GET {path}: {data}")
        return data

    async def _post(self, path: str, payload: dict):
        r = await self.cli.post(path, json=payload)
        r.raise_for_status()
        data = r.json()
        ui.notify(f"POST {path}: {data}")
        return data

    async def test_backend(self):
        ui.notify(BACKEND_URL)
        ui.notify(API_KEY)
        floors = await backend.list_floors()
        print("Floors:", floors)

        rooms = await backend.list_rooms(1)
        print("Rooms:", rooms)
        room_extended_id = int(1) * int(100) + int(2)
        devices = await backend.list_devices(1, room_extended_id)
        print("Devices:", devices)

    async def list_floors(self):
        return (await self._get("/floors/list"))["floors"]
    async def create_floor(self, payload):
        return await self._post("/floors/create", payload)
    async def list_rooms(self, floor: int):
        return (await self._get(f"/floors/{floor}/rooms/list"))["rooms"]
    async def create_room(self, floor: int, payload):
        return await self._post(f"/floors/{floor}/rooms/create", {"rooms":[payload]})
    async def list_devices(self, floor: int, room: str):
        return (await self._get(f"/floors/{floor}/rooms/{room}/devices/list"))["devices"]





backend = BackendClient(BACKEND_URL, API_KEY)


# ------------------------------------------------------------------
# 2. Pydantic view‑models
# ------------------------------------------------------------------
class RoomVM(BaseModel):
    room_number: str
    room_type: str
    capacity: int
    is_occupied: bool
    device_count: int

class DeviceVM(BaseModel):
    device_id: str
    device_type: str
    is_online: bool
    last_seen: str | None = None

# ------------------------------------------------------------------
# 3. Admin dashboard
# ------------------------------------------------------------------
@ui.page("/admin")
async def admin_dashboard():
    ui.markdown("## 🏨 Admin Dashboard")


    ui.button("Test API", on_click=backend.test_backend)
    # ---- UI scaffold -----------------------------------------------------
    floor_select = ui.select([], label="Floor")
    table = ui.table(columns=[
        {"name":"room_number","label":"Room","field":"room_number"},
        {"name":"room_type","label":"Type","field":"room_type"},
        {"name":"is_occupied","label":"Occupied","field":"is_occupied"},
        {"name":"device_count","label":"Devices","field":"device_count"},
    ], rows=[], row_key="room_number", selection="single")

    # ---- helpers ---------------------------------------------------------
    async def refresh_rooms(floor: int):
        rooms = await backend.list_rooms(floor)
        table.rows = [RoomVM(**r).dict() for r in rooms]
        table.update()

    async def refresh_floors():
        options = [f["floor_number"] for f in await backend.list_floors()]
        floor_select.options = options; floor_select.update()
        if options:
            floor_select.value = options[0]
            await refresh_rooms(options[0])

    async def seed_data():
        # Create Floor 1 with Rooms 1–10
        await backend.create_floor({
            "floor_number": 1,
            "floor_name": "Floor 1",
            "rooms": []
        })
        for r in range(1, 11):
            room_extended_id = int(1) * int(100) + r
            await backend.create_room(1, {
                "room_number": str(room_extended_id),
                "room_type": "Standard",
                "capacity": 2
            })

        # Create Floor 2 with Rooms 1–8
        await backend.create_floor({
            "floor_number": 2,
            "floor_name": "Floor 2",
            "rooms": []
        })
        for r in range(1, 9):
            room_extended_id = int(2) * int(100) + r
            await backend.create_room(2, {
                "room_number": str(room_extended_id),
                "room_type": "Standard",
                "capacity": 2
            })

        await refresh_floors()
        ui.notify("Seeded Floor 1→Rooms 1–10 and Floor 2→Rooms 1–8")

    ui.button("Seed Sample Data", color="secondary", on_click=seed_data)

    def to_room(e):
        if e.args and floor_select.value is not None:
            ui.open(f"/room/{floor_select.value}/{e.args['room_number']}")

    # ---- wire actions ----------------------------------------------------
    # ui.button("➕ Add floor", color="primary", on_click=add_floor_dialog)
    # ui.button("➕ Add room",  on_click=add_room_dialog)
    floor_select.on("update:model-value", lambda e: refresh_rooms(int(e.value)))
    table.on("select", to_room)

    # await refresh_floors()

# ------------------------------------------------------------------
# 4. Guest view
# ------------------------------------------------------------------
@ui.page("/room/{floor:int}/{room}")
async def room_dashboard(floor: int, room: str):
    ui.markdown(f"### Room {room} (Floor {floor}) – Guest view")
    table = ui.table(columns=[
        {"name":"device_id","label":"ID","field":"device_id"},
        {"name":"device_type","label":"Type","field":"device_type"},
        {"name":"is_online","label":"Online","field":"is_online"},
        {"name":"last_seen","label":"Last seen","field":"last_seen"},
    ], rows=[], row_key="device_id")

    async def refresh():
        devs = await backend.list_devices(floor, room)
        table.rows = [DeviceVM(**d).dict() for d in devs]; table.update()
    ui.timer(5.0, refresh)
    await refresh()

# ------------------------------------------------------------------
# 5. Landing page
# ------------------------------------------------------------------
ui.page("/")(lambda: ui.markdown("Welcome – use `/admin` or `/room/1/101`"))


ui.run(title="SCIoT Hotel UI")
