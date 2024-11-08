import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';

void main() => runApp(const MyApp());

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  List<BluetoothDevice> _devices = [];
  BluetoothDevice? _selectedDevice;
  late BluetoothConnection connection;
  List<String> messages = [];
  final TextEditingController _textController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadDevices();
  }

  Future<void> _loadDevices() async {
    List<BluetoothDevice> devices = await FlutterBluetoothSerial.instance.getBondedDevices();
    setState(() {
      _devices = devices;
      if (_devices.isNotEmpty) {
        _selectedDevice = _devices.first;
      }
    });
  }

  Future<void> _sendData(String data) async {
    data = data.trim();
    try {
      List<int> list = data.codeUnits;
      Uint8List bytes = Uint8List.fromList(list);
      connection.output.add(bytes);
      await connection.output.allSent;
      setState(() {
        messages.add("Me: $data");
      });
      if (kDebugMode) {
        print('Data sent successfully');
      }
    } catch (e) {
      print(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: const Text("Bluetooth Chat"),
        ),
        body: Column(
          children: [
            if (_devices.isNotEmpty)
              DropdownButton<BluetoothDevice>(
                value: _selectedDevice,
                onChanged: (BluetoothDevice? newValue) {
                  setState(() {
                    _selectedDevice = newValue!;
                  });
                },
                items: _devices.map<DropdownMenuItem<BluetoothDevice>>((BluetoothDevice device) {
                  return DropdownMenuItem<BluetoothDevice>(
                    value: device,
                    child: Text(device.name ?? device.address),
                  );
                }).toList(),
              )
            else
              const Text("No bonded devices found"),
            ElevatedButton(
              child: const Text("Connect"),
              onPressed: () {
                if (_selectedDevice != null) {
                  _connect(_selectedDevice!.address);
                }
              },
            ),
            const SizedBox(height: 10.0),
            Expanded(
              child: ListView.builder(
                itemCount: messages.length,
                itemBuilder: (context, index) {
                  return ListTile(
                    title: Text(messages[index]),
                  );
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      decoration: const InputDecoration(
                        labelText: 'Enter message',
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: () {
                      if (_textController.text.isNotEmpty) {
                        _sendData(_textController.text);
                        _textController.clear();
                      }
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _connect(String address) async {
    try {
      connection = await BluetoothConnection.toAddress(address);
      _sendData('Connected');
      connection.input!.listen((Uint8List data) {
        String receivedData = String.fromCharCodes(data);
        setState(() {
          messages.add("Device: $receivedData");
        });
      });
    } catch (exception) {
      print("Cannot connect, exception occurred: $exception");
    }
  }
}
