from __future__ import annotations
import asyncio
from typing import Any

from nicegui import ui
from pydantic import BaseModel
from backend_client import Backend


backend = Backend()

# Data models
class RoomVM(BaseModel):
    id:str|None=None
    room_number: str
    room_type: str | None = None
    capacity: int| None = None
    is_occupied: bool| None = None
    created_at:str| None = None
    last_cleaned:str| None = None
    floor_number:int|None = None
    floor_name:str| None = None
    devices:list = []
    @property
    def device_count(self): return len(self.devices)

class DeviceVM(BaseModel):
    id: str
    device_id: str
    name: str
    device_type: str
    is_online: bool
    description: str | None = None
    last_seen: str | None = None
    created_at: str | None = None
    type_name: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    unit: str | None = None
    last_value: str | None = None
    last_value_simplified: int | None = None
    last_value_simplified_string: str | None = None
    is_off: bool | None = None
    ai_planing_type: str | None = None

class StepVM(BaseModel):
    id: int
    step_order: int
    action_name: str
    raw_step: str
    target_device_ids: List[str]

class PlanVM(BaseModel):
    id: int
    scope: str
    target_floor_id: int
    target_room_id: str
    total_cost: float
    planning_time: float
    planner_used: Optional[str]
    raw_plan: List[str]
    created_at: str
    filtered_plan: Optional[List[str]] = None
    cleaning_plan: Optional[List[str]] = None
    steps: List[StepVM]


# State
current_floor:int|None=None
current_rooom_dbclick = None
view_whole_building:bool=True
rows_known:set[str]=set()
device_timer=None

# Header
def add_header(role: str = "Admin") -> None:
    with ui.header(elevated=False).classes("bg-primary text-white items-center"):
        ui.icon("domain").classes("mr-2")
        ui.label("SCIoT Hotel").classes("text-h6")
        ui.label(role).classes("ml-auto text-sm text-white opacity-75")

# Room detail area
async def show_room(summary_column, floor_no:int, room:dict):
    global device_timer
    if device_timer: device_timer.cancel(); device_timer=None
    summary_column.clear(); vm=RoomVM.model_validate(room)
    devices_known:set[str]=set()
    async def refresh_devices():
            nonlocal devices_known

            devs = await backend.list_devices(floor_no, vm.room_number)
            simplified_map = {-1: "Low", 0: "Medium", 1: "High"}
            rows = []
            for d in devs:
                try:
                    d['last_value'] = f"{float(d['last_value']):.2f}"
                except (ValueError, TypeError):
                    pass
                simplified_numeric = d.get('last_value_simplified')
                d['last_value_simplified_string'] = simplified_map.get(simplified_numeric, "")
                rows.append(DeviceVM.model_validate(d).model_dump())

            ids={r["device_id"] for r in rows}
            if ids!=devices_known:
                grid_dev.options["rowData"]=rows; grid_dev.update(); devices_known=ids
            else:
                for row in rows:
                    for k,v in row.items():
                        grid_dev.run_row_method(row["device_id"],"setDataValue",k,v)

    with summary_column.style("width:50%"):
        with ui.card().props("flat bordered").style("width:100%"):
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

                        {"headerName":"Name","field":"name", "width": 150},
                        {"headerName":"Type","field":"type_name", "width": 120},
                        {"headerName":"Simplified","field":"last_value_simplified_string", "headerTooltip": "The simplified high/low value (-1, 0, 1)", "width": 120},
                        {"headerName":"AI Type","field":"ai_planing_type", "width": 120},
                        {"headerName":"Online","field":"is_online", "width": 100},
                        {"headerName":"Last Seen","field":"last_seen"},
                        {"headerName":"Device ID","field":"device_id"},
                        # {"headerName":"Raw Value", "field":"last_value"},
                        # {"headerName":"Unit", "field":"unit"},
                        {"headerName":"Is Off", "field":"is_off"},
                        {"headerName":"Description", "field":"description"},
                        # {"headerName":"Min Value", "field":"min_value"},
                        # {"headerName":"Max Value", "field":"max_value"},
                        # {"headerName":"Created On", "field":"created_at"},
                        # {"headerName":"Category", "field":"device_type"},
                        # {"headerName":"Internal ID", "field":"id"},
                    ],
                    "defaultColDef":{"flex":1,"resizable":True, "sortable": True},
                    "rowData":[],
                    ":getRowId":"(p)=>p.data.device_id",
                }
            ).style("min-height:300px")

        device_timer = ui.timer(10.0, lambda: asyncio.create_task(refresh_devices()))
    await refresh_devices()

async def show_latest_plan_for_room(room_number: str):
    res = await backend.get_latest_plan_for_room(room_number)
    # validate and notify each step…
    plan_vm = PlanVM.model_validate(res['latest_plan'])
    for step in plan_vm.steps:
        ui.notify(f"Step {step.step_order}: {step.action_name}", timeout=2.0)

# Admin page
@ui.page("/admin")
async def admin_dashboard():
    global view_whole_building, current_floor, rows_known

    add_header()
    await backend.seed_if_needed()
    floors=await backend.list_floors(); floors.sort(key=lambda f:f["floor_number"])

    rows_known.clear()
    ui.button('Wipe DB', on_click = backend.clear_database)

    with ui.row().style("width:100%") as main_row:

        with ui.column().style("width:48%") as left_col:   # whole left panel
            with ui.card().props("flat bordered").style("width:100%"):
                # toggle at very top
                toggle = ui.toggle(["Building","Floor"],
                                value="Building" if view_whole_building else "Floor",
                                on_change=lambda e: asyncio.create_task(toggle_view(e.value))
                                ).props("dense")

                # per-floor sub-panel
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

                # building grid
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

                async def run_plan_for_room(room_number):

                    sel = await grid_building.run_grid_method('getSelectedRows') or await grid_per_floor.run_grid_method('getSelectedRows')
                    room_number = sel[0]['room_number']
                    ui.notify(f'Running planner for room {room_number}…')
                    res = await backend.run_planner_for_room(room_number)
                    if 'error' in res:
                        ui.notify(f"Planner error: {res['error']}", color='negative')
                    else:
                        ui.notify('Planner started', color='positive')

                with ui.row().classes("items-center"):
                    ui.icon("auto_awesome").classes("text-primary")
                    ui.label("Planner").classes("text-h6 text-primary")
                chips_row = ui.row().classes('gap-2 mt-2 rounded-lg border border-primary').style('padding: 0.5rem')
                with chips_row:
                        ui.chip('No rooms selected',
                        color='grey-5',
                        text_color='white').props('outline square')
                # Action buttons below chips_row
                with ui.row().classes("gap-2 mt-4"):
                    # Cleaning Actions
                     ui.button('Run Planner for Selected Room', on_click=run_plan_for_room)

                    # ui.button('Send Cleaning Team', on_click=lambda: None)
                    # ui.button('Clean Rooms', on_click=lambda: None)
                    # # Energy Optimization Actions
                    # ui.button('Save Energy', on_click=lambda: None)
                    # ui.button('Cancel Out Actuators', on_click=lambda: None)

        summary_column = ui.column()   # right pane


    # helper refresh routines




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

        chips_row.clear()
        if not sel:
            with chips_row:
                ui.chip('No rooms selected',
                        color='grey-5',
                        text_color='white').props('outline square')
            return

        with chips_row:
            for r in sel:
                ui.chip(f"Room {r['room_number']}").props('outline square')

    def on_cell_double_clicked(e):
        global current_rooom_dbclick
        current_rooom_dbclick = e.args['data']['is_occupied']
        # ui.notify(e.args['data'])
        ui.navigate.to(f"/guest/{e.args['data']['floor_number'] or current_floor}/{e.args['data']['room_number']}", new_tab=True)

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

    # toggle behaviour
    async def toggle_view(label:str):
        nonlocal_label = label  # keep mypy happy
        show_building = (nonlocal_label == "Building")
        per_floor_panel.visible = not show_building
        grid_building.visible  =     show_building
        rows_known.clear(); chips_row.clear()
        if show_building:
            await refresh_building()
        else:
            await load_floor(1)

    # initial visibility & data
    per_floor_panel.visible = False if view_whole_building else True
    grid_building.visible   = True  if view_whole_building else False

    if view_whole_building:
        await refresh_building()
    else:
        current_floor = floors[0]["floor_number"]
        await load_floor(1)

    # periodic refresh (25 s)
    async def poll():
        if grid_building.visible: await refresh_building()
        else:                     await refresh_per_floor()

    ui.timer(5.0, lambda: asyncio.create_task(poll()))



# Guest page
@ui.page("/guest/{floor:int}/{room}")
async def guest_view(floor: int, room: str, ):
    global current_rooom_dbclick
    # add_header("Guest")
    ui.label(f"Room {room} (Floor {floor})").classes("text-h5 q-ma-md")
    async def handle_switch():
        global current_rooom_dbclick
        await backend.set_room_occupancy(floor, room, not current_rooom_dbclick)
        current_rooom_dbclick = not current_rooom_dbclick

    ui.switch("Occupied", value=current_rooom_dbclick, on_change=handle_switch)

    # The dialog logic remains the same as it already handles both device types.
    async def show_device_dialog(e):
        # ui.notify(e)
        # The event now directly passes the row data dictionary.
        _, device_data, _ = e.args
        device = DeviceVM.model_validate(device_data)

        with ui.dialog() as dialog, ui.card():
            ui.label(f"Device: {device.name}").classes("text-h6")

            if device.device_type == 'actuator':
                ui.label("Set new value:")
                try:
                    current = not device.is_off
                except (ValueError, TypeError):
                    # current_val = device.min_value or 0.0
                    pass


                slider = ui.slider(
                    min=0.0,
                    max=1.0,
                    value=current
                ).props('label-always')

                # toggle =  ui.switch("Toggle", value=True)

                with ui.row().classes('w-full justify-end'):
                    async def handle_done():
                        await backend.set_actuator_value(device.device_id, slider.value)
                        ui.notify(f"Setting {device.name} to {slider.value:.2f}")
                        await refresh_guest_devices() # Refresh to see the change
                        dialog.close()

                    ui.button("Done", on_click=handle_done)
                    ui.button("Cancel", on_click=dialog.close)
            else:

                ui.label("Set new value:")
                try:
                    current_val = float(device.last_value)
                except (ValueError, TypeError):
                    current_val = device.min_value or 0.0

                slider = ui.slider(
                    min=device.min_value or 0.0,
                    max=device.max_value or 100.0,
                    value=current_val
                ).props('label-always')

                with ui.row().classes('w-full justify-end'):
                    async def handle_done():
                        await backend.set_sensor_value(device.device_id, slider.value)
                        # await backend.set_actuator_value(device.device_id, slider.value)
                        ui.notify(f"Setting {device.name} to {slider.value:.2f}")
                        await refresh_guest_devices() # Refresh to see the change
                        dialog.close()

                    ui.button("Done", on_click=handle_done)
                    ui.button("Cancel", on_click=dialog.close)

                # ui.label(f"Last reported value: {device.last_value} {device.unit or ''}")
                # with ui.row().classes('w-full justify-end'):
                #     ui.button("Close", on_click=dialog.close)

        await dialog

    # sensors and actuator tables
    with ui.row().classes('w-full justify-around'):

        # --- Sensors Column ---
        with ui.row():
            with ui.column():
                ui.label('Sensors').classes('text-h6')
                sensor_table = ui.table(
                    columns=[
                        {"name": "name", "label": "Device", "field": "name", "align": "left"},
                        {"name": "last_value", "label": "Value", "field": "last_value", "align": "center"},
                        {"name": "last_value_simplified", "label": "Status", "field": "last_value_simplified_string", "align": "center"},
                        {"name": "is_online", "label": "Online", "field": "is_online", "align": "center"},
                        # {"name": "unit", "label": "unit", "field": "unit", "align": "center"},
                    ],
                    rows=[], row_key="device_id",
                ).classes('w-full')

            # --- Actuators Column ---
            with ui.column():
                ui.label('Actuators').classes('text-h6')
                actuator_table = ui.table(
                    columns=[
                        {"name": "name", "label": "Device", "field": "name", "align": "left"},
                        {"name": "last_value", "label": "Value", "field": "last_value", "align": "center"},
                        {"name": "is_off", "label": "State", "field": "is_off", "align": "center"},
                        {"name": "is_online", "label": "Online", "field": "is_online", "align": "center"},
                        # {"name": "unit", "label": "unit", "field": "unit", "align": "center"},
                    ],
                    rows=[], row_key="device_id",
                ).classes('w-full')
        #                     # planning card

            sensor_table.add_slot('body-cell-last_value_simplified', r'''
                <q-td :props="props">
                    <q-badge v-if="['Low','Medium','High'].includes(props.value)"
                            :color="props.value==='Low'  ? 'green-6'
                                    :props.value==='High' ? 'red-6'
                                                        : 'orange-6'">
                        {{ props.value }}
                    </q-badge>
                    <span v-else>{{ props.value }}</span>
                </q-td>
            ''')


            actuator_table.add_slot('body-cell-is_off', r'''
                <q-td :props="props">
                    <q-badge :color="props.value ? 'grey-5' : 'light-green-5'">
                        {{ props.value ? 'Off' : 'On' }}
                    </q-badge>
                </q-td>
            ''')

            online_offline_icon_slot = r'''
                <q-td :props="props">
                <q-icon
                    v-if="props.value"
                    name="lens"
                    size="9px"
                    color="green-3"
                />
                <q-icon
                    v-else
                    name="lens"
                    size="9px"
                    color="grey-4"
                />
                </q-td>

            '''
            sensor_table.add_slot('body-cell-is_online', online_offline_icon_slot)
            actuator_table.add_slot('body-cell-is_online', online_offline_icon_slot)


            # Assign the same event handler to both tables
            sensor_table.on('row-dblclick',  show_device_dialog)
            actuator_table.on('row-dblclick', show_device_dialog)
    #         with ui.column():
    # # Action buttons below chips_row
    #             with ui.row().classes("gap-2 mt-4"):
    #                 # Cleaning Actions
    #                 ui.button('Send Cleaning Team', on_click=lambda: None)
    #                 ui.button('Clean Rooms', on_click=lambda: None)
    #                 # Energy Optimization Actions
    #                 ui.button('Save Energy', on_click=lambda: None)
    #                 ui.button('Cancel Out Actuators', on_click=lambda: None)
        ui.space()

    async def refresh_guest_devices():
        devs = await backend.list_devices(floor, room)

        sensor_rows = []
        actuator_rows = []
        simplified_map = {-1: "Low", 0: "Medium", 1: "High"}

        for d in devs:
            try:
                d['last_value'] = f"{float(d['last_value']):.2f}"
            except (ValueError, TypeError):
                pass

            simplified_numeric = d.get('last_value_simplified')
            d['last_value_simplified_string'] = simplified_map.get(simplified_numeric, "N/A")

            device_data = DeviceVM.model_validate(d).model_dump(exclude_none=True)

            if device_data['device_type'] == 'sensor':
                sensor_rows.append(device_data)
            else:
                actuator_rows.append(device_data)

        sensor_table.rows = sensor_rows
        actuator_table.rows = actuator_rows

        sensor_table.update()
        actuator_table.update()

    await refresh_guest_devices()
    ui.timer(3.0, lambda: asyncio.create_task(refresh_guest_devices()))


ui.run(title="SCIoT Hotel UI")
