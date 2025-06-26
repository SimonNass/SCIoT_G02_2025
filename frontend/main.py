from __future__ import annotations

# ─────────────────────────  SCIoT Hotel Monitor (NiceGUI)  ────────────────────
# Default view  : WHOLE BUILDING
# Toggle switch : Building  ↔  Per-floor
# ──────────────────────────────────────────────────────────────────────────────
import asyncio
import os
import random
from typing import Any

import httpx
from dotenv import load_dotenv
from nicegui import ui
from pydantic import BaseModel

# ──────────  CONFIG  ──────────
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost").rstrip("/")
API_KEY     = os.getenv("API_KEY",     "changeme")

# ──────────  BACKEND CLIENT  ──────────
class Backend:
    def __init__(self) -> None:
        self.cli = httpx.AsyncClient(
            base_url=BACKEND_URL,
            headers={"X-API-Key": API_KEY},
            timeout=10,
        )

    async def _get (self, p:str)                -> Any:  r = await self.cli.get (p); r.raise_for_status(); return r.json()
    async def _post(self, p:str, payload:dict)  -> Any:  r = await self.cli.post(p, json=payload); (r.raise_for_status() if r.status_code!=409 else None); return r.json()

    async def list_floors(self):           return (await self._get("/floors/list"))["floors"]
    async def list_rooms (self, floor:int):return (await self._get(f"/floors/{floor}/rooms/list"))["rooms"]
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

backend = Backend()

# ──────────  DATA MODELS  ──────────
class RoomVM(BaseModel):
    id:str|None=None; room_number:str; room_type:str|None=None; capacity:int|None=None
    is_occupied:bool|None=None; created_at:str|None=None; last_cleaned:str|None=None
    floor_number:int|None=None; floor_name:str|None=None; devices:list=[]
    @property
    def device_count(self): return len(self.devices)

class DeviceVM(BaseModel):
    id:str; device_id:str; name:str; device_type:str; is_online:bool
    description:str|None=None; last_seen:str|None=None; created_at:str

# ──────────  GLOBAL STATE  ──────────
current_floor:int|None=None
view_whole_building:bool=True              # ← default
rows_known:set[str]=set()
device_timer=None                          # refresh timer in room pane

# ──────────  HEADER  ──────────
def add_header(role: str = "Admin") -> None:
    with ui.header(elevated=False).classes("bg-primary text-white items-center"):
        ui.icon("domain").classes("mr-2")
        ui.label("SCIoT Hotel").classes("text-h6")
        ui.label(role).classes("ml-auto text-sm text-white opacity-75")

# ──────────  ROOM DETAIL PANE  ──────────
async def show_room(summary_column, floor_no:int, room:dict):
    global device_timer
    if device_timer: device_timer.cancel(); device_timer=None
    summary_column.clear(); vm=RoomVM.model_validate(room)
    devices_known:set[str]=set()
    async def refresh_devices():
            nonlocal devices_known
            devs = await backend.list_devices(floor_no, vm.room_number)
            rows=[DeviceVM.model_validate(d).model_dump() for d in devs]
            ids={r["device_id"] for r in rows}
            if ids!=devices_known:
                grid_dev.options["rowData"]=rows; grid_dev.update(); devices_known=ids
            else:
                for row in rows:
                    for k,v in row.items():
                        grid_dev.run_row_method(row["device_id"],"setDataValue",k,v)
    # simple
    # async def refresh_devices():
    #     devs=await backend.list_devices(floor_no, vm.room_number)
    #     rows=[DeviceVM.model_validate(d).model_dump() for d in devs]
    #     grid_dev.options["rowData"]=rows; grid_dev.update()

    with summary_column.style("width:50%"):
        with ui.card().props("flat bordered").style("width:100%"):
            # ui.label(f"Room {vm.room_number}").classes("text-h6 text-primary")
            # ui.label("Planner").classes("text-h6 text-primary")
            ui.markdown(f"###### Room {vm.room_number}").classes("text-primary text-md")
            with ui.row().classes("gap-2"):
                ui.chip("Occupied", icon="hotel",
                        color="red" if vm.is_occupied else "green").props("outline square")
                ui.chip(vm.room_type or "-", icon="info",
                        color="cyan").props("outline square")
                ui.chip(f"Capacity: {vm.capacity}", icon="group",
                        color="blue").props("outline square")
                ui.chip(f"Devices: {vm.device_count}", icon="devices",
                        color="purple").props("outline square")

            ui.markdown("###### Devices").classes("text-primary text-md")
            grid_dev = ui.aggrid(
                {
                    "columnDefs":[
                        {"headerName":"ID","field":"device_id"},
                        {"headerName":"Name","field":"name"},
                        {"headerName":"Type","field":"device_type"},
                        {"headerName":"Description","field":"description"},
                        {"headerName":"Online","field":"is_online"},
                        {"headerName":"Last Seen","field":"last_seen"},
                    ],
                    "defaultColDef":{"flex":1,"resizable":True},
                    "rowData":[],
                    ":getRowId":"(p)=>p.data.device_id",
                }
            ).style("min-height:300px")

        device_timer = ui.timer(10.0, lambda: asyncio.create_task(refresh_devices()))
    await refresh_devices()

# ──────────  ADMIN PAGE  ──────────
@ui.page("/admin")
async def admin_dashboard():
    global view_whole_building, current_floor, rows_known

    add_header()
    await backend.seed_if_needed()
    floors=await backend.list_floors(); floors.sort(key=lambda f:f["floor_number"])

    rows_known.clear()

    # ───── layout scaffold ─────
    with ui.row().style("width:100%") as main_row:

        with ui.column().style("width:48%") as left_col:   # whole left panel
            with ui.card().props("flat bordered").style("width:100%"):
                # toggle at very top
                toggle = ui.toggle(["Building","Floor"],
                                value="Building" if view_whole_building else "Floor",
                                on_change=lambda e: asyncio.create_task(toggle_view(e.value))
                                ).props("dense")

                # ───── per-floor sub-panel (can hide) ─────
                per_floor_panel = ui.column().style("width:100%")
                with per_floor_panel:
                    with ui.row().classes("items-center gap-3"):
                        ui.icon("layers").classes("text-primary")
                        ui.label("Floor").classes("text-h6 text-primary")
                        pager = ui.pagination(1, len(floors), direction_links=False)\
                                .classes("shadow-md rounded-lg")
                    floor_info = ui.row().classes("gap-2")

                    grid_per_floor = ui.aggrid(
                        {
                            "rowSelection":"multiple",
                            "suppressRowClickSelection":True,
                            "columnDefs":[
                                {"headerName":"Room","field":"room_number","checkboxSelection":True,"width":125},
                                {"headerName":"Type","field":"room_type","width":100},
                                {"headerName":"Capacity","field":"capacity","width":100},
                                {"headerName":"Occupancy","field":"is_occupied","width":120},
                                {"headerName":"Last Cleaned","field":"last_cleaned","width":130},
                                {"headerName":"Created","field":"created_at","width":130},
                            ],
                            "defaultColDef":{"flex":1,"resizable":True},
                            "rowData":[],
                            ":getRowId":"(p)=>p.data.room_number",
                        }
                    ).style("min-height:300px")

                # ───── building grid (always in left column) ─────
                grid_building = ui.aggrid(
                    {
                        "rowSelection":"multiple",
                        "suppressRowClickSelection":True,
                        "columnDefs":[
                            {"headerName":"Floor","field":"floor_number","checkboxSelection":True,"width":90,"sortable":True},
                            {"headerName":"Room","field":"room_number","width":125,"sortable":True},
                            {"headerName":"Type","field":"room_type","width":100},
                            {"headerName":"Capacity","field":"capacity","width":100},
                            {"headerName":"Occupancy","field":"is_occupied","width":120},
                            {"headerName":"#Devices","field":"device_count","width":120},
                            {"headerName":"Created","field":"created_at","width":130},
                        ],
                        "defaultColDef":{"flex":1,"resizable":True},
                        "rowData":[],
                        ":getRowId":"(p)=>p.data.id",
                    }
                ).style("min-height:300px")

            # planning card
            with ui.card().props("flat bordered").style("width:100%"):
                with ui.row().classes("items-center"):
                    ui.icon("auto_awesome").classes("text-primary")
                    ui.label("Planner").classes("text-h6 text-primary")
                chips_row = ui.row().classes('gap-2 mt-2 rounded-lg border border-primary').style('padding: 0.5rem')
                with chips_row:
                        ui.chip('No rooms selected',
                        color='grey-5',
                        text_color='white').props('outline square')
                # -- place chips in chips_row if you have any --

                # Action buttons below chips_row
                with ui.row().classes("gap-2 mt-4"):
                    # Cleaning Actions
                    ui.button('Send Cleaning Team', on_click=lambda: None)
                    ui.button('Clean Rooms', on_click=lambda: None)

                    # Assignment Actions
                    # ui.button('Assign Room to Floor', on_click=lambda: None)
                    # ui.button('Assign Device to Room Position', on_click=lambda: None)

                    # Actuator/Sensor Controls
                    # ui.button('Turn On Actuator', on_click=lambda: None)
                    # ui.button('Turn Off Actuator', on_click=lambda: None)
                    # ui.button('Turn On (Inverted)', on_click=lambda: None)
                    # ui.button('Turn Off (Inverted)', on_click=lambda: None)
                    # ui.button('Increase Sensor Value', on_click=lambda: None)
                    # ui.button('Decrease Sensor Value', on_click=lambda: None)

                    # Activity/State Recognition


                    # Energy Optimization Actions
                    ui.button('Save Energy', on_click=lambda: None)
                    ui.button('Cancel Out Actuators', on_click=lambda: None)

        summary_column = ui.column()   # right pane

    # helper refresh routines -------------------------------------------------
    async def refresh_building():
        global rows_known
        data = await backend.list_all_rooms()
        rows=[]
        for r in data:
            d = RoomVM.model_validate(r).model_dump()
            d["created_at"] = (d["created_at"] or "")[:10]
            rows.append(d)
        ids={r["id"] for r in rows}
        if ids!=rows_known:
            grid_building.options["rowData"]=rows; grid_building.update(); rows_known=ids
        else:
            for r in rows:
                for k,v in r.items():
                    grid_building.run_row_method(r["id"],"setDataValue",k,v)

    async def refresh_per_floor():
        global rows_known
        if current_floor is None: return
        data = await backend.list_rooms(current_floor)
        rows=[RoomVM.model_validate(r).model_dump()|{"created_at":(r.get("created_at") or "")[:10]}
              for r in data]
        ids={r["room_number"] for r in rows}
        if ids!=rows_known:
            grid_per_floor.options["rowData"]=rows; grid_per_floor.update(); rows_known=ids
        else:
            for r in rows:
                for k,v in r.items():
                    grid_per_floor.run_row_method(r["room_number"],"setDataValue",k,v)

    # chip helper
    async def update_chips(grid):
        sel = await grid.run_grid_method('getSelectedRows')

        chips_row.clear()                       # always keep the row itself
        if not sel:
            with chips_row:                                # no selection → placeholder chip
                ui.chip('No rooms selected',
                        color='grey-5',
                        text_color='white').props('outline square')
            return

        with chips_row:                         # otherwise show the real chips
            for r in sel:
                ui.chip(f"Room {r['room_number']}").props('outline square')

    def on_cell_double_clicked(e):
        ui.notify(e.args['data'])
        if view_whole_building:
            ui.navigate.to(f"/guest/{e.args['data']['floor_number']}/{e.args['data']['room_number']}", new_tab=True)
        else:
            ui.navigate.to(f"/guest/{current_floor}/{e.args['data']['room_number']}", new_tab=True)
        # do your navigation here

    # grid event wiring
    grid_building.on("selectionChanged", lambda e: asyncio.create_task(update_chips(grid_building)))
    grid_building.on('cellDoubleClicked', on_cell_double_clicked)

    grid_per_floor.on("selectionChanged", lambda e: asyncio.create_task(update_chips(grid_per_floor)))
    grid_per_floor.on('cellDoubleClicked', on_cell_double_clicked)

    grid_building.on("cellClicked",
        lambda e: asyncio.create_task(show_room(summary_column, e.args["data"]["floor_number"], e.args["data"])))
    grid_per_floor.on("cellClicked",
        lambda e: asyncio.create_task(show_room(summary_column, current_floor, e.args["data"])))

    # pager behaviour
    async def load_floor(page:int):
        global current_floor, rows_known
        f=floors[page-1]; current_floor=f["floor_number"]; rows_known.clear()
        await refresh_per_floor()
        floor_info.clear()
        with floor_info:
            ui.chip(f'{f["floor_name"]}',icon="domain",color="cyan").props("outline square")
            ui.chip(f'{f["description"]}',icon="info",color="green").props("outline square")
            ui.chip(f'Total Rooms: {len(f["rooms"])}',icon="meeting_room",color="purple").props("outline square")

    pager.on("update:model-value", lambda e: asyncio.create_task(load_floor(int(e.args))))

    # toggle behaviour --------------------------------------------------------
    async def toggle_view(label:str):
        nonlocal_label = label  # keep mypy happy
        show_building = (nonlocal_label == "Building")
        per_floor_panel.visible = not show_building
        grid_building.visible  =     show_building
        rows_known.clear(); chips_row.clear()
        if show_building:
            await refresh_building()
        else:
            await load_floor(1)   # reset to first floor

    # initial visibility & data ----------------------------------------------
    per_floor_panel.visible = False if view_whole_building else True
    grid_building.visible   = True  if view_whole_building else False

    if view_whole_building:
        await refresh_building()
    else:
        current_floor = floors[0]["floor_number"]
        await load_floor(1)

    # periodic refresh (25 s) -------------------------------------------------
    async def poll():
        if grid_building.visible: await refresh_building()
        else:                     await refresh_per_floor()
    ui.timer(25.0, lambda: asyncio.create_task(poll()))

# ──────────  GUEST VIEW  ──────────
import asyncio, json
from aiomqtt import Client as MQTT           # ← new import
# ... any other imports (DeviceVM, backend, add_header, ui) ...

BROKER_HOST = "localhost"
BROKER_PORT = 1883

@ui.page("/guest/{floor:int}/{room}")
async def guest_view(floor: int, room: str):
    add_header("Guest")
    ui.label(f"Room {room} (Floor {floor})")

    # metadata + live-value table
    tbl = ui.table(
        columns=[
            {"name": "device_id",   "label": "ID",        "field": "device_id"},
            {"name": "device_type", "label": "Type",      "field": "device_type"},
            {"name": "is_online",   "label": "Online",    "field": "is_online"},
            {"name": "last_seen",   "label": "Last seen", "field": "last_seen"},
            {"name": "value",       "label": "Live",      "field": "value"},
        ],
        rows=[], row_key="device_id",
    )

    # periodically refresh static info
    async def refresh_meta():
        devs = await backend.list_devices(floor, room)
        for d in devs:
            d["value"] = "—"                       # placeholder
        tbl.rows = [DeviceVM.model_validate(d).model_dump() for d in devs]
        tbl.update()
        return [d["device_id"] for d in devs]      # return list of IDs

    device_ids = await refresh_meta()
    ui.timer(10.0, lambda: asyncio.create_task(refresh_meta()))

    # ── live MQTT listener ────────────────────────────────────────────────
    async def mqtt_listener(ids: list[str]):
        async with MQTT(BROKER_HOST, BROKER_PORT) as client:

            # subscribe once for every device topic
            for did in ids:
                await client.subscribe(f"devices/{did}/status")

            # ← NEW: iterate directly over client.messages
            async for msg in client.messages:
                try:
                    ui.notify(msg)
                    data = json.loads(msg.payload.decode())
                except Exception:

                    continue

                device_id = msg.topic.split("/")[1]
                value     = data.get("value", "—")

                tbl.run_method(
                    "updateCell",
                    {"rowKey": device_id, "field": "value", "value": value},
                )




    asyncio.create_task(mqtt_listener(device_ids))

# ──────────  LAUNCH APP  ──────────
ui.run(title="SCIoT Hotel UI")
