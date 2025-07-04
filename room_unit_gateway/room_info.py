
class Room_Info():
    def __init__(self, floor_id: int, max_rooms_per_floor: int, room_id: int):
        self.floor_id = floor_id
        self.max_rooms_per_floor = max_rooms_per_floor
        self.room_id = room_id
        self.room_extended_id = int(floor_id) * int(max_rooms_per_floor) + int(room_id)
