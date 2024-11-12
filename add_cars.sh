#!/bin/bash

# Fiesta variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Fiesta","year":2020,"price":12500,"transmission":"Manual","mileage":25000,"fuelType":"Petrol","tax":150,"mpg":55.4,"engineSize":1.0}'
echo -e "\nFiesta 1.0 added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Fiesta","year":2021,"price":14500,"transmission":"Automatic","mileage":18000,"fuelType":"Petrol","tax":155,"mpg":52.3,"engineSize":1.1}'
echo -e "\nFiesta 1.1 added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Fiesta ST","year":2022,"price":22000,"transmission":"Manual","mileage":8000,"fuelType":"Petrol","tax":165,"mpg":45.6,"engineSize":1.5}'
echo -e "\nFiesta ST added"

# Focus variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Focus","year":2021,"price":18500,"transmission":"Manual","mileage":15000,"fuelType":"Petrol","tax":165,"mpg":50.2,"engineSize":1.5}'
echo -e "\nFocus 1.5 added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Focus","year":2022,"price":21000,"transmission":"Automatic","mileage":12000,"fuelType":"Diesel","tax":155,"mpg":58.8,"engineSize":2.0}'
echo -e "\nFocus Diesel added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Focus ST","year":2023,"price":34000,"transmission":"Manual","mileage":5000,"fuelType":"Petrol","tax":185,"mpg":35.7,"engineSize":2.3}'
echo -e "\nFocus ST added"

# Puma variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Puma","year":2023,"price":22500,"transmission":"Manual","mileage":5000,"fuelType":"Petrol","tax":155,"mpg":52.3,"engineSize":1.0}'
echo -e "\nPuma 1.0 added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Puma","year":2022,"price":24500,"transmission":"Automatic","mileage":8000,"fuelType":"Hybrid","tax":145,"mpg":58.9,"engineSize":1.0}'
echo -e "\nPuma Hybrid added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Puma ST","year":2023,"price":32000,"transmission":"Manual","mileage":3000,"fuelType":"Petrol","tax":170,"mpg":42.8,"engineSize":1.5}'
echo -e "\nPuma ST added"

# Kuga variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Kuga","year":2022,"price":28000,"transmission":"Manual","mileage":12000,"fuelType":"Diesel","tax":155,"mpg":54.3,"engineSize":1.5}'
echo -e "\nKuga Diesel added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Kuga","year":2023,"price":32000,"transmission":"Automatic","mileage":8000,"fuelType":"Hybrid","tax":145,"mpg":48.7,"engineSize":2.0}'
echo -e "\nKuga Hybrid added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Kuga PHEV","year":2023,"price":38000,"transmission":"Automatic","mileage":5000,"fuelType":"Hybrid","tax":0,"mpg":201.8,"engineSize":2.5}'
echo -e "\nKuga PHEV added"

# Mustang variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Mustang","year":2021,"price":45000,"transmission":"Manual","mileage":12000,"fuelType":"Petrol","tax":580,"mpg":25.7,"engineSize":5.0}'
echo -e "\nMustang GT Manual added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Mustang","year":2022,"price":48000,"transmission":"Automatic","mileage":8000,"fuelType":"Petrol","tax":580,"mpg":24.8,"engineSize":5.0}'
echo -e "\nMustang GT Auto added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Mustang Mach-E","year":2023,"price":55000,"transmission":"Automatic","mileage":5000,"fuelType":"Electric","tax":0,"mpg":379.0,"engineSize":0.0}'
echo -e "\nMustang Mach-E added"

# Explorer variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Explorer","year":2022,"price":58000,"transmission":"Automatic","mileage":15000,"fuelType":"Petrol","tax":580,"mpg":25.7,"engineSize":3.0}'
echo -e "\nExplorer Petrol added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Explorer","year":2023,"price":65000,"transmission":"Automatic","mileage":8000,"fuelType":"Hybrid","tax":150,"mpg":35.3,"engineSize":3.0}'
echo -e "\nExplorer Hybrid added"

# Ranger variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Ranger","year":2022,"price":32000,"transmission":"Manual","mileage":20000,"fuelType":"Diesel","tax":290,"mpg":35.3,"engineSize":2.0}'
echo -e "\nRanger Diesel added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Ranger Raptor","year":2023,"price":48000,"transmission":"Automatic","mileage":5000,"fuelType":"Diesel","tax":290,"mpg":32.1,"engineSize":3.0}'
echo -e "\nRanger Raptor added"

# Transit Custom variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Transit Custom","year":2022,"price":28000,"transmission":"Manual","mileage":25000,"fuelType":"Diesel","tax":275,"mpg":40.9,"engineSize":2.0}'
echo -e "\nTransit Custom added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Transit Custom PHEV","year":2023,"price":42000,"transmission":"Automatic","mileage":8000,"fuelType":"Hybrid","tax":0,"mpg":91.7,"engineSize":1.0}'
echo -e "\nTransit Custom PHEV added"

# Tourneo variants
curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Tourneo Custom","year":2022,"price":38000,"transmission":"Automatic","mileage":15000,"fuelType":"Diesel","tax":275,"mpg":38.2,"engineSize":2.0}'
echo -e "\nTourneo Custom added"

curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
-d '{"model":"Tourneo Connect","year":2023,"price":32000,"transmission":"Manual","mileage":8000,"fuelType":"Diesel","tax":155,"mpg":45.6,"engineSize":1.5}'
echo -e "\nTourneo Connect added"

echo -e "\nAll cars have been added successfully!"