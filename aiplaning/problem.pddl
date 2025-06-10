; SCIoT_G02_2025 example problem

(define (problem example)

(:domain SCIoT_G02_2025)

(:objects
    floor1 floor2 - floor
    elevator room1 room2 room3 room4 room5 room6 room7 room8 room9 room10 - room
    room11 room12 room13 room14 room15 room16 room17 room18 room19 room20 - room
    cleaning_team1 cleaning_team2 - cleaning_team

    temperatur - temperature_s
    lights1 lights2 - virtual_switch_s
    
    green_led blue_led red_led - light_switch_a
    heater ac - numerical_a
)

(:init
    ;; room topology

    ; needed for cleaning_team
    (room_is_part_of_floor elevator floor1)
    (room_is_part_of_floor elevator floor2)
    (is_next_to room1 elevator)
    (is_next_to room5 elevator)
    (is_cleaned elevator)
    (is_at cleaning_team1 room1)
    (is_at cleaning_team2 room1)
    
    (room_is_part_of_floor room1 floor2)
    (room_is_part_of_floor room2 floor2)
    (room_is_part_of_floor room3 floor2)
    (room_is_part_of_floor room4 floor2)
    (room_is_part_of_floor room5 floor1)
    (room_is_part_of_floor room6 floor1)
    (room_is_part_of_floor room7 floor1)
    (room_is_part_of_floor room8 floor1)
    (room_is_part_of_floor room9 floor1)
    (room_is_part_of_floor room10 floor1)
    
    (is_next_to room1 room2)
    (is_next_to room2 room3)
    (is_next_to room3 room4)
    (is_next_to room4 room1)
    ;(is_next_to room4 room5)
    (is_next_to room5 room6)
    (is_next_to room6 room7)
    (is_next_to room7 room9)
    ;(is_next_to room8 room9)
    (is_next_to room9 room10)
    
    (is_next_to room1 room10)
    



    ;(is_next_to room4 room7)
    ;(is_next_to room3 room8)
    ;(is_next_to room2 room9)
    ;(is_next_to room1 room10)


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
 
    ;; context

    ; raw sensor data
    ;(is_low temperatur)
    (is_high temperatur)

    ; raw actuator data
    (is_activated green_led)

    ; meta context
    (is_ocupied room1)

    ; activitys
    (is_doing_read room1)
    ;(not (is_ocupied room2))
    ;(is_doing_sleep room2)

    ; supresses cleaning planing
    ;(is_cleaned room1)
    ;(is_cleaned room2)
    ;(is_cleaned room3)
    ;(is_cleaned room4)
    ;(is_cleaned room5)
    ;(is_cleaned room6)
    ;(is_cleaned room7)
    ;(is_cleaned room8)
    ;(is_cleaned room9)
    ;(is_cleaned room10)
    ;(is_cleaned room11)
    ;(is_cleaned room12)
    ;(is_cleaned room13)
    ;(is_cleaned room14)
    ;(is_cleaned room15)
    ;(is_cleaned room16)
    ;(is_cleaned room17)
    ;(is_cleaned room18)
    ;(is_cleaned room19)
    ;(is_cleaned room20)
)

(:goal
    (and
        ; specific goals for ocupied rooms
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

        ; general goals for all unocupied rooms
        (forall (?room - room) 
            (imply  
                (and
                    ; defines goal of all unocupied rooms
                    (not (is_ocupied ?room))
                    ; exceptions ignore these rooms in the forall
                    (not (= ?room room10)) 
                )
                (and
                    ; clean the room
                    (is_cleaned ?room )
                    ; turn off all actuators
                    (forall (?actuator - actuator) 
                        (imply  (actuator_is_part_of_room ?actuator ?room)
                            (not (is_activated ?actuator))
                        )
                    ) 
                )
            )
        )
        ; enforce some checks
        (forall (?room - room) 
            (fulfilled_activity ?room)
        )
    )
)

)