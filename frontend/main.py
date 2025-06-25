# nicegui_app.py – extended version
from __future__ import annotations
import os, asyncio
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel
from nicegui import ui

load_dotenv()
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost').rstrip('/')
API_KEY     = os.getenv('API_KEY', 'changeme')

# ------------------------------------------------------------------
# 1. REST helper client
# ------------------------------------------------------------------
class BackendClient:
    def __init__(self):
        self.cli = httpx.AsyncClient(
            base_url=BACKEND_URL,
            headers={'X-API-Key': API_KEY},
            timeout=10,
        )

    async def _get(self, path: str):
        r = await self.cli.get(path); r.raise_for_status(); return r.json()

    async def _post(self, path: str, payload: dict):
        r = await self.cli.post(path, json=payload)
        if r.status_code != 409:
            r.raise_for_status()
        return r.json()

    async def list_floors(self):
        return (await self._get('/floors/list'))['floors']

    async def list_rooms(self, floor: int):
        return (await self._get(f'/floors/{floor}/rooms/list'))['rooms']

    async def list_devices(self, floor: int, room: str):
        return (await self._get(f'/floors/{floor}/rooms/{room}/devices/list'))['devices']

    async def seed_if_needed(self):
        floors = await self.list_floors()
        if floors:
            return
        for current_floor_number, count in [(1, 10), (2, 8)]:
            await self._post('/floors/create', {
                'floor_number': current_floor_number,
                'floor_name': f'Floor {current_floor_number}',
                'description': f'Description for Floor {current_floor_number}',
                'rooms': []
            })
            for n in range(1, count + 1):
                await self._post(f'/floors/{current_floor_number}/rooms/create', {
                    'rooms': [{
                        'room_number': f'{current_floor_number}{n:02d}',
                        'room_type': 'Standard',
                        'capacity': 2
                    }]
                })

backend = BackendClient()

# ------------------------------------------------------------------
# 2. View-models
# ------------------------------------------------------------------
class FloorVM(BaseModel):
    id: int
    floor_number: int
    floor_name: str
    description: str
    created_at: str
    total_rooms: int

class RoomVM(BaseModel):
    id: str
    room_number: str
    room_type: str
    capacity: int
    is_occupied: bool
    last_cleaned: str | None = None
    created_at: str
    devices: list = []

    @property
    def device_count(self) -> int:
        return len(self.devices)

class DeviceVM(BaseModel):
    id: str  # Unique identifier for the device
    device_id: str  # Device UUID
    name: str  # Name of the device
    device_type: str  # Type of the device (e.g., sensor, actuator)
    description: str | None = None  # Optional description of the device
    is_online: bool  # Online status of the device
    last_seen: str | None = None  # Last time the device was seen online
    created_at: str  # Timestamp when the device was created

# ------------------------------------------------------------------
# 3. Layout helpers
# ------------------------------------------------------------------
def add_header():
    with ui.header(elevated=False).classes('bg-primary text-white items-center'):
        ui.icon('hotel').classes('mr-2')
        ui.label('SCIoT Hotel Monitor').classes('text-h6')

@ui.page('/admin')
async def admin_dashboard():
    add_header()
    await backend.seed_if_needed()

    floors = await backend.list_floors()
    if not floors:
        ui.notify('No floors available.')
        return
    max_page = len(floors)

    with ui.row().classes('items-center gap-2'):
        ui.icon('layers').classes('text-primary')
        ui.label('Floor').classes('text-lg text-primary')
        pager = ui.pagination(1, max_page, direction_links=False).classes('shadow-md rounded-lg')

    with ui.row().style('width:100%') as splitter:
        with ui.card().props('flat bordered').style('width:40%'):
            floor_info_column = ui.row().classes('gap-2')  # Floor info section above the room list
            grid = ui.aggrid({
                'defaultColDef': {'flex': 1},
                'rowSelection': 'single',
                'columnDefs': [
                    {'headerName': 'Room',      'field': 'room_number', 'width': 75},
                    {'headerName': 'Type',      'field': 'room_type',   'width': 100},
                    {'headerName': 'Capacity',  'field': 'capacity',    'width': 100},
                    {'headerName': 'Occupancy', 'field': 'is_occupied', 'width': 120},
                    {'headerName': 'Last Cleaned', 'field': 'last_cleaned', 'width': 130},
                    {'headerName': 'Created',   'field': 'created_at',  'width': 130},
                ],
                'defaultColDef': {
                    'resizable': True
                },
                'rowData': []
            }).style('min-height:300px')

        summary_column = ui.column()

    async def load_floor(page: int):
        global current_floor_number
        floor = floors[page - 1]  # Get the current floor data
        current_floor_number = floor['floor_number']

        floor_description = floor['description']
        rooms = await backend.list_rooms(current_floor_number)
        total_rooms = len(rooms)

        # Update floor info dynamically
        floor_info_column.clear()
        with floor_info_column:
            ui.chip(f'Floor {current_floor_number}', icon='layers', color='blue').props('outline square')
            ui.chip(f'Description: {floor_description}', icon='info', color='green').props('outline square')
            ui.chip(f'Total Rooms: {total_rooms}', icon='meeting_room', color='purple').props('outline square')

        # Update grid with room data
        rows = [
            RoomVM.model_validate(r).model_dump() | {'created_at': r['created_at'][:10]}  # Format date to show only YYYY-MM-DD
            for r in rooms
        ]
        grid.options['rowData'] = rows
        grid.update()

    def on_cell_click(event):
        row = event.args.get('data')
        if row:
            asyncio.create_task(show_room(summary_column, current_floor_number, row))

    pager.on('update:model-value', lambda e: asyncio.create_task(load_floor(int(e.args))))
    grid.on('cellClicked', on_cell_click)

    await load_floor(1)

    # def show_room(panel, room_json: dict):
    #     panel.clear()
    #     vm = RoomVM.parse_obj(room_json)

    #     with panel.style('width:50%'):
    #         with ui.card().props('flat bordered'):
    #             ui.markdown(f'###### Room {vm.room_number}').classes('text-primary text-md')
    #             with ui.row().classes('gap-2'):
    #                 ui.chip('Occupied', icon='hotel', color='red' if vm.is_occupied else 'green').props('outline square')
    #                 ui.chip(f'Capacity: {vm.capacity}', icon='group', color='blue').props('outline square')
    #                 ui.chip(f'Devices: {vm.device_count}', icon='devices', color='purple').props('outline square')
    #                 ui.chip(f'Last Cleaned: {vm.last_cleaned}', icon='cleaning_services', color='orange').props('outline square')

    #             ui.markdown('###### Devices').classes('text-primary text-md')
    #             columns = [
    #                 {'headerName': 'ID',        'field': 'device_id'},
    #                 {'headerName': 'Type',      'field': 'device_type', 'sortable': True},
    #                 {'headerName': 'Online',    'field': 'is_online',   'sortable': True},
    #                 {'headerName': 'Last Seen', 'field': 'last_seen',   'sortable': True, 'width': 300},
    #             ]
    #             rows = [DeviceVM.parse_obj(d).dict() for d in vm.devices]
    #             ui.aggrid({
    #                 'defaultColDef': {'flex': 1},
    #                 'columnDefs': columns,
    #                 'rowData': rows,
    #             })

    async def show_room(panel, floor_number: int, room_data: dict):
        panel.clear()
        vm = RoomVM.model_validate(room_data)
        async def refresh_devices():
            try:
                # Fetch devices using the list_devices method
                devices = await backend.list_devices(floor_number, vm.room_number)
                rows = [DeviceVM.model_validate(d).model_dump() for d in devices]
                device_grid.options['rowData'] = rows
                device_grid.update()
            except Exception as e:
                ui.notify(f'Failed to fetch devices: {str(e)}', type='error')

        # Display room details
        with panel.style('width:50%'):
            with ui.card().props('flat bordered'):
                ui.markdown(f'###### Room {vm.room_number}').classes('text-primary text-md')
                with ui.row().classes('gap-2'):
                    ui.chip('Occupied', icon='hotel', color='red' if vm.is_occupied else 'green').props('outline square')
                    ui.chip(f'Capacity: {vm.capacity}', icon='group', color='blue').props('outline square')
                    ui.chip(f'Devices: {vm.device_count}', icon='devices', color='purple').props('outline square')
                    ui.chip(f'Last Cleaned: {vm.last_cleaned}', icon='cleaning_services', color='orange').props('outline square')


                ui.markdown('###### Devices').classes('text-primary text-md')
                device_grid = ui.aggrid({
                    'defaultColDef': {'flex': 1},
                    'columnDefs': [
                        {'headerName': 'ID',        'field': 'device_id'},
                        {'headerName': 'Name',      'field': 'name'},
                        {'headerName': 'Type',      'field': 'device_type'},
                        {'headerName': 'Description','field': 'description'},
                        {'headerName': 'Online',    'field': 'is_online'},
                        {'headerName': 'Last Seen', 'field': 'last_seen'},
                    ],
                    'rowData': []
                }).style('min-height:300px')

                # Periodically refresh the device list
                with panel:  # Ensure the timer is created within the correct UI context
                    ui.timer(5.0, refresh_devices)

        await refresh_devices()


# ------------------------------------------------------------------
# 5.  Guest room page (unchanged)
# ------------------------------------------------------------------
@ui.page('/room/{floor:int}/{room}')
async def room_page(floor: int, room: str):
    add_header()
    ui.label(f'Room {room} (Floor {floor})')
    table = ui.table(
        columns=[
            {'name':'device_id','label':'ID','field':'device_id'},
            {'name':'device_type','label':'Type','field':'device_type'},
            {'name':'is_online','label':'Online','field':'is_online'},
            {'name':'last_seen','label':'Last seen','field':'last_seen'},
        ],
        rows=[], row_key='device_id'
    )
    async def refresh_devices():
        devs = await backend.list_devices(floor, room)
        table.rows = [DeviceVM.parse_obj(d).dict() for d in devs]
        table.update()

    ui.timer(5.0, refresh_devices)
    await refresh_devices()

# ------------------------------------------------------------------
# 6.  Landing & run
# ------------------------------------------------------------------
ui.page('/')(lambda: ui.link('→ Admin dashboard', '/admin').classes('text-xl'))
ui.run(title='SCIoT Hotel UI')
