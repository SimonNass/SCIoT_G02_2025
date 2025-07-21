from __future__ import annotations
import asyncio
from typing import Any, List, Optional

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
    device_count: int

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
    id: str
    step_order: int
    action_name: str
    raw_step: str
    target_device_ids: List[str]

class PlanVM(BaseModel):
    id: str
    scope: str
    target_floor_id: Optional[str] = None
    target_room_id: Optional[str] = None
    total_cost: Optional[float] = None
    planning_time: Optional[float] = None
    planner_used: Optional[str] = None
    raw_plan: Optional[List[str] | str] = None
    created_at: str
    filtered_plan: Optional[List[List[str]]] = None
    cleaning_plan: Optional[List[List[str]]] = None
    detected_activity_plan: Optional[List[List[str]]] = None
    steps: List[StepVM]


# State
current_floor:int|None=None
view_whole_building:bool=True
rows_known:set[str]=set()
device_timer=None
plan_timer=None
selected_rows=[]
viewed_room_number: str | None = None
# Header
def add_header(role: str = "Admin") -> None:
    with ui.header(elevated=False).classes("bg-primary text-white items-center"):
        ui.icon("domain").classes("mr-2")
        ui.label("SCIoT Hotel").classes("text-h6")
        ui.label(role).classes("ml-auto text-sm text-white opacity-75")

# Room detail area
async def show_room(summary_column, floor_no:int, room:dict, fetch_plan_on_load: bool = False):
    global device_timer, plan_timer, selected_rows, viewed_room_number
    if device_timer: device_timer.cancel()
    if plan_timer: plan_timer.cancel()
    viewed_room_number = room['room_number']

    summary_column.clear()
    vm = RoomVM.model_validate(room)
    devices_known: set[str] = set()

    # The refresh functions now accept the UI element they need to modify.
    async def refresh_devices(grid: ui.aggrid):
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

        ids = {r["device_id"] for r in rows}
        if ids != devices_known:
            # We don't need `with grid:` here because we are calling a method on the element itself.
            grid.options["rowData"] = rows
            grid.update()
            devices_known = ids
        else:
            for row in rows:
                for k, v in row.items():
                    grid.run_row_method(row["device_id"], "setDataValue", k, v)

    async def refresh_plan(container: ui.column):
        # We must enter the container's context before manipulating it or creating notifications.

        with container:
            # ui.notify("starting planning")
            try:

                room_number = selected_rows[0]['room_number']
                res = await backend.get_latest_plan_for_room(room_number)
                ui.notify(f"Latest plan for room: {res}")
                plan_vm = PlanVM.model_validate(res['latest_plan'])

                container.clear()
                # Display the header chips with plan metadata
                with ui.row().classes("gap-2"):
                    ui.chip(f"Planner: {plan_vm.planner_used or 'N/A'}", icon="memory", color="blue").props("outline square")
                    ui.chip(f"Time: {plan_vm.planning_time or 0:.2f}s", icon="timer", color="green").props("outline square")
                    ui.chip(f"Cost: {plan_vm.total_cost or 0}", icon="paid", color="orange").props("outline square")
                    ui.chip(f"Created: {plan_vm.created_at[11:19]}", icon="today", color="purple").props("outline square")


                has_any_content = False

                if plan_vm.steps:
                    has_any_content = True
                    ui.markdown("###### Steps").classes("text-primary text-md mt-4")
                    
                    with ui.list().props("bordered separator"):
                        # ui.notify(plan_vm.steps)
                        for step in sorted(plan_vm.steps, key=lambda s: s.step_order):
                            with ui.item():
                                with ui.item_section().props("avatar"):
                                    ui.chip(f"{step.step_order}", color="primary", text_color="white")
                                with ui.item_section():
                                    ui.item_label(step.action_name.replace('_', ' ').title())
                                    ui.item_label(f"({step.raw_step})").props("caption")

                # filtered plan (the actual actions)
                if plan_vm.filtered_plan:
                    has_any_content = True
                    ui.markdown("###### Plan Actions").classes("text-primary text-md mt-4")
                    with ui.list().props("bordered separator"):
                        for i, action_string in enumerate(plan_vm.filtered_plan):
                            with ui.item():
                                with ui.item_section().props("avatar"):
                                    ui.chip(f"{i + 1}", color="primary", text_color="white")
                                with ui.item_section():
                                    ui.item_label(action_string).style('font-family: monospace')

                # detected activities
                if plan_vm.detected_activity_plan:
                    has_any_content = True
                    ui.markdown("###### Detected Activities").classes("text-primary text-md mt-4")
                    with ui.list().props("bordered separator"):
                        for activity in plan_vm.detected_activity_plan:
                            with ui.item():
                                with ui.item_section().props("avatar"):
                                    ui.icon("visibility", color="primary")
                                with ui.item_section():
                                    ui.item_label(" ".join(activity).replace('_', ' ').title())

                # cleaning plan
                if plan_vm.cleaning_plan:
                    has_any_content = True
                    ui.markdown("###### Cleaning Instructions").classes("text-primary text-md mt-4")
                    with ui.list().props("bordered separator"):
                        for instruction in plan_vm.cleaning_plan:
                            with ui.item():
                                with ui.item_section().props("avatar"):
                                    ui.icon("cleaning_services", color="primary")
                                with ui.item_section():
                                    ui.item_label(" ".join(instruction).replace('_', ' ').title())


                if not has_any_content:
                    with ui.list().props("bordered"):
                         ui.item_label("Plan found, but it contains no actions or instructions.").classes('q-pa-md')

            except Exception as e:
                container.clear()
                ui.label("No plan available for this room.").classes("text-grey q-pa-md")


    with summary_column.style("width:50%"):
        with ui.card().props("flat bordered").style("width:100%"):
            ui.markdown(f"###### Room {vm.room_number}").classes("text-primary text-md")
            with ui.row().classes("gap-2"):
                ui.chip(f"{'Occupied' if vm.is_occupied else 'Vacant'}",
                        icon=f"{'person' if vm.is_occupied else 'person_outline'}",
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

        with ui.card().props("flat bordered").style("width:100%"):
            ui.markdown("###### Latest AI Plan").classes("text-primary text-md")
            plan_container = ui.column().style("width:100%")



    with summary_column:
        device_timer = ui.timer(10.0, lambda: refresh_devices(grid_dev))
        if fetch_plan_on_load:
            plan_timer = ui.timer(10.0, lambda: asyncio.create_task(refresh_plan(plan_container)), immediate=False)
            # inital plan
            await refresh_plan(plan_container)

    # Perform initial load
    await refresh_devices(grid_dev)



# Admin page
@ui.page("/admin")
async def admin_dashboard():
    global view_whole_building, current_floor, rows_known

    add_header()
    # await backend.seed_if_needed()
    floors=await backend.list_floors(); floors.sort(key=lambda f:f["floor_number"])

    rows_known.clear()
    ui.button('Wipe DB', on_click = backend.clear_database)

    ui.button('Seed DB', on_click = backend.seed_if_needed)

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
                                # {"headerName":"Occupancy","field":"is_occupied","width":120},
                                {
                                    "headerName": "Occupancy", "field": "is_occupied", "width": 120,
                                    "editable": True, # Make the cell interactive
                                    "cellRenderer": 'agCheckboxCellRenderer' # Tell it to render as a checkbox
                                },
                                # {"headerName":"Last Cleaned","field":"last_cleaned","width":130},
                                # {"headerName":"Created","field":"created_at","width":130},
                            ],
                            "defaultColDef":{"flex":1,"resizable":True},
                            "rowData":[],
                            ":getRowId":"(p)=>p.data.room_number",
                        }
                    ).style("min-height:300px")

                # building grid
                grid_building = ui.aggrid(
                    {
                        "rowSelection":"single",
                        "suppressRowClickSelection":True,
                        "columnDefs":[
                            {"headerName":"Floor","field":"floor_number","checkboxSelection":True,"width":90,"sortable":True},
                            {"headerName":"Room","field":"room_number","width":125,"sortable":True},
                            {"headerName":"Type","field":"room_type","width":100},
                            {"headerName":"Capacity","field":"capacity","width":100},
                            # {"headerName":"Occupancy","field":"is_occupied","width":120},
                            {
                                "headerName": "Occupancy", "field": "is_occupied", "width": 120,
                                "editable": True, # Make the cell interactive
                                "cellRenderer": 'agCheckboxCellRenderer' # Tell it to render as a checkbox
                            },
                            # {"headerName":"#Devices","field":"device_count","width":120},
                            # {"headerName":"Created","field":"created_at","width":130},
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
                        ui.notify(f"Planner finished: {res}", color='positive')
                        floor_number = sel[0].get('floor_number') or current_floor
                        await show_room(summary_column, floor_number, sel[0], fetch_plan_on_load=True)


                with ui.row().classes("items-center"):
                    # ui.icon("auto_awesome").classes("text-primary")
                    ui.separator().classes("text-h6 text-primary")

                chips_row = ui.row().classes('gap-2 mt-2 rounded-lg border border-primary').style('padding: 0.5rem')
                with chips_row:
                        ui.chip('No rooms selected',
                        color='grey-5',
                        text_color='white').props('outline square')

                with ui.row().classes("gap-2 mt-4"):
                     ui.button('Run Planner', on_click=run_plan_for_room)
                    #  ui.button('Toggle Occupancy', on_click=toggle_occupancy, color='secondary')
           # Thresholds card
            with ui.card().props("flat bordered").style("width:100%"):
                with ui.row().classes("items-center"):
                    ui.icon("tune").classes("text-primary")
                    ui.label("Sensor Thresholds").classes("text-h6 text-primary")

                async def save_changes(e):
                    # When a cell value is changed, this event is fired
                    row = e.args['data']
                    # ui.notify(f"Updating thresholds for {row['type_name']}...")
                    try:
                        await backend.set_type_name_config(
                            row['device_type'],
                            row['type_name'],
                            float(row['lower_mid_limit']),
                            float(row['upper_mid_limit'])
                        )
                        # ui.notify(f"Successfully updated {row['type_name']}.", color='positive')
                    except Exception as ex:
                        ui.notify(f"Error updating: {ex}", color='negative')

                threshold_grid = ui.aggrid({
                    "columnDefs": [
                        {"headerName": "Sensor Type", "field": "type_name", "width": 150, "editable": False},
                        {"headerName": "Low-Mid Threshold", "field": "lower_mid_limit", "editable": True},
                        {"headerName": "Mid-High Threshold", "field": "upper_mid_limit", "editable": True},
                        {"headerName": "Unit", "field": "unit", "editable": False},
                    ],
                    "defaultColDef": {"flex": 1},
                    "rowData": [],
                    ":getRowId": "(p) => p.data.id",
                }).on('cellValueChanged', save_changes)

            async def refresh_thresholds():
                configs = await backend.list_type_name_configs()
                threshold_grid.options['rowData'] = configs
                threshold_grid.update()

            # Add a timer to periodically refresh the thresholds
            ui.timer(60.0, refresh_thresholds)
            await refresh_thresholds()

        summary_column = ui.column()


    async def handle_occupancy_edit(e):
        global viewed_room_number # Access the global state
        try:
            row_data = e.args['data']
            new_status = row_data['is_occupied']
            room_number = row_data['room_number']
            floor_number = row_data.get('floor_number') or current_floor
            await backend.set_room_occupancy(floor_number, room_number, new_status)
            if room_number == viewed_room_number:
                 await show_room(summary_column, floor_number, row_data)

        except Exception as ex:
            # ui.notify(f"Error updating occupancy: {ex}", color='negative')
            if grid_building.visible: await refresh_building()
            else: await refresh_per_floor()


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
        global selected_rows
        sel = await grid.run_grid_method('getSelectedRows')
        selected_rows = sel
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
        # ui.notify(e.args['data'])
        ui.navigate.to(f"/guest/{e.args['data']['floor_number'] or current_floor}/{e.args['data']['room_number']}", new_tab=True)

    # grid event wiring
    grid_building.on("selectionChanged", lambda e: asyncio.create_task(update_chips(grid_building)))
    grid_building.on('cellDoubleClicked', on_cell_double_clicked)
    grid_building.on('cellValueChanged', handle_occupancy_edit)


    grid_per_floor.on("selectionChanged", lambda e: asyncio.create_task(update_chips(grid_per_floor)))
    grid_per_floor.on('cellDoubleClicked', on_cell_double_clicked)

    grid_building.on("cellClicked",
        lambda e: asyncio.create_task(show_room(summary_column, e.args["data"]["floor_number"], e.args["data"])))
    grid_per_floor.on("cellClicked",
        lambda e: asyncio.create_task(show_room(summary_column, current_floor, e.args["data"])))
    grid_per_floor.on('cellValueChanged', handle_occupancy_edit)

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
async def guest_view(floor: int, room: str):
    add_header("Guest")
    ui.label(f"Room {room} (Floor {floor})").classes("text-h5 q-ma-md")

    async def show_device_dialog(e):
        _, device_data, _ = e.args
        device = DeviceVM.model_validate(device_data)

        with ui.dialog() as dialog, ui.card():
            ui.label(f"Device: {device.name}").classes("text-h6")
            if device.device_type == 'actuator':
                ui.label("Set new value:")
                try:
                    current = not device.is_off
                except (ValueError, TypeError):
                    pass
                slider = ui.slider(min=0.0, max=1.0, value=current).props('label-always')
                with ui.row().classes('w-full justify-end'):
                    async def handle_done():
                        await backend.set_actuator_value(device.device_id, slider.value)
                        ui.notify(f"Setting {device.name} to {slider.value:.2f}")
                        await refresh_guest_devices()
                        dialog.close()
                    ui.button("Done", on_click=handle_done)
                    ui.button("Cancel", on_click=dialog.close)
            else:
                ui.label("Set new value:")
                try:
                    current_val = float(device.last_value)
                except (ValueError, TypeError):
                    current_val = device.min_value or 0.0
                slider = ui.slider(min=device.min_value or 0.0, max=device.max_value or 100.0, value=current_val).props('label-always')
                with ui.row().classes('w-full justify-end'):
                    async def handle_done():
                        await backend.set_sensor_value(device.device_id, slider.value)
                        ui.notify(f"Setting {device.name} to {slider.value:.2f}")
                        await refresh_guest_devices()
                        dialog.close()
                    ui.button("Done", on_click=handle_done)
                    ui.button("Cancel", on_click=dialog.close)
        await dialog

    async def show_trend_chart(e):
        sensor = e.args
        sensor_id = sensor['device_id']
        sensor_name = sensor['name']
        sensor_unit = sensor.get('unit', '')

        with ui.dialog() as dialog, ui.card().style('min-width: 700px'):
            ui.label(f"Recent History for {sensor_name}").classes('text-h6')

            chart_options = {
                'tooltip': {'trigger': 'axis'},
                'xAxis': {'type': 'time'},
                'yAxis': {'type': 'value', 'name': sensor_unit},
                'series': [{'name': sensor_unit, 'data': [], 'type': 'line', 'smooth': True}],
            }
            # using ui.echart
            chart = ui.echart(chart_options).classes('w-full h-64')

            dialog.open()
            try:
                # fetch recent data from the backend
                res = await backend.get_recent_sensor_data(sensor_id, minutes=5, interval=1)
                sensor_data = res.get('sensor_data', [])

                # process the data into a format ECharts can understand
                chart_data = [[item['timestamp'], item['value']] for item in sensor_data]

                # update the echart with the fetched data
                chart.options['series'][0]['data'] = chart_data
                chart.update()

            except Exception as ex:
                ui.notify(f"Could not load history: {ex}", color='negative')

    with ui.row().classes('w-full justify-around'):
        with ui.row():
            with ui.column():
                ui.label('Sensors').classes('text-h6')
                sensor_table = ui.table(
                    columns=[
                        {"name": "name", "label": "Device", "field": "name", "align": "left"},
                        {"name": "last_value", "label": "Value", "field": "last_value", "align": "center"},
                        {"name": "last_value_simplified", "label": "Status", "field": "last_value_simplified_string", "align": "center"},
                        {"name": "trend", "label": "Trend", "field": "trend", "align": "center"},
                        {"name": "is_online", "label": "Online", "field": "is_online", "align": "center"},
                    ],
                    rows=[], row_key="device_id",
                ).classes('w-full')
            with ui.column():
                ui.label('Actuators').classes('text-h6')
                actuator_table = ui.table(
                    columns=[
                        {"name": "name", "label": "Device", "field": "name", "align": "left"},
                        {"name": "last_value", "label": "Value", "field": "last_value", "align": "center"},
                        {"name": "is_off", "label": "State", "field": "is_off", "align": "center"},
                        {"name": "is_online", "label": "Online", "field": "is_online", "align": "center"},
                    ],
                    rows=[], row_key="device_id",
                ).classes('w-full')

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
                <q-icon v-if="props.value" name="lens" size="9px" color="green-3" />
                <q-icon v-else name="lens" size="9px" color="grey-4" />
                </q-td>
            '''
            sensor_table.add_slot('body-cell-is_online', online_offline_icon_slot)
            actuator_table.add_slot('body-cell-is_online', online_offline_icon_slot)
            sensor_table.add_slot('body-cell-trend', r'''
                <q-td :props="props">
                    <q-btn flat dense round icon="show_chart" @click="$parent.$emit('show-trend', props.row)" />
                </q-td>
            ''')

            sensor_table.on('show-trend', show_trend_chart)
            sensor_table.on('row-dblclick',  show_device_dialog)
            actuator_table.on('row-dblclick', show_device_dialog)
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

@ui.page('/')
def index_page():
    ui.navigate.to('/admin')

ui.run(title="SCIoT Hotel UI")