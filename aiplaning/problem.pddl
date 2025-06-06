; SCIoT_G02_2025 example problem

(define (problem example)

(:domain SCIoT_G02_2025)
    (:requirements :disjunctive-preconditions)

(:objects
    floor1 - floor
    room1 room2 room3 room4 - room

    temperatur - temperature_s
    lights1 lights2 - virtual_switch_s
    
    green_led blue_led red_led - light_switch_a
    heater ac - numerical_a
)

(:init
    ; room topology
    (room_is_part_of_floor room1 floor1)
    (room_is_part_of_floor room2 floor1)
    
    (is_next_to room2 room1)
    (is_next_to room2 room3)

    (sensor_is_part_of_room temperatur room1)
    (sensor_is_part_of_room lights1 room1)
    (sensor_is_part_of_room lights2 room2)
  
    (actuator_is_part_of_room green_led room1)
    (actuator_is_part_of_room blue_led room1)
    (actuator_is_part_of_room red_led room1)
    (actuator_is_part_of_room heater room1)
    (actuator_is_part_of_room ac room1)
    
    ; sensor actuator mapping
    (actuator_increases_sensor heater temperatur)
    (actuator_decreases_sensor ac temperatur)
    (actuator_increases_sensor green_led lights1)
    (actuator_increases_sensor blue_led lights1)
    (actuator_increases_sensor red_led lights1)
 
    ; context
    ; raw sensor data
    ;(is_low temperatur)
    (is_high temperatur)

    ; raw actuator data
    (is_activated green_led)

    ; meta context
    (is_ocupied room1)
    ;(is_doing_read room1)
    ;(not (is_ocupied room2))
    ;(is_doing_sleep room2)
)

(:goal
    (and
        (imply (is_ocupied room1)
            (and
                (is_ok temperatur)
                (is_sensing lights1)   
            )
        )

        (imply (is_ocupied room2)
            (and  
                (is_sensing lights2)
            )
        )

        (forall (?room - room) 
            (imply  (not (is_ocupied ?room))
                (is_cleaned ?room )
            )
        )
    )
)
)