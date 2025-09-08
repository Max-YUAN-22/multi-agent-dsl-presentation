# agents/parking_agent.py
from core.base_agent import BaseAgent

class ParkingAgent(BaseAgent):
    def __init__(self, dsl_instance):
        super().__init__(dsl_instance, 'parking', ['update_parking_status', 'adjust_parking_fee'])

    def update_parking_status(self, data):
        """
        Updates the status information of the parking lot.
        """
        print(f"Parking status updated at {data['location']}. Available spots: {data['available_spots']}")
        self.adjust_parking_fee(data)

    def adjust_parking_fee(self, data):
        """
        Adjusts parking fees based on parking availability.
        """
        if data['available_spots'] < 5:
            print(f"Increasing parking fee at {data['location']}.")
        else:
            print(f"Parking fee remains normal at {data['location']}.")
