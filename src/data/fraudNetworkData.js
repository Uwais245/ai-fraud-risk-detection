export const fraudNetworkData = {
  nodes: [
    {
      id: "customer-1",
      type: "fraud",
      position: { x: 40, y: 100 },
      data: {
        type: "Customer",
        value: "CUST-1029",
        risk: 64,
      },
    },

    {
      id: "customer-2",
      type: "fraud",
      position: { x: 40, y: 300 },
      data: {
        type: "Customer",
        value: "CUST-1042",
        risk: 82,
      },
    },

    {
      id: "customer-3",
      type: "fraud",
      position: { x: 40, y: 500 },
      data: {
        type: "Customer",
        value: "CUST-1077",
        risk: 28,
      },
    },

    {
      id: "device-1",
      type: "fraud",
      position: { x: 350, y: 180 },
      data: {
        type: "Device",
        value: "DEV-204",
      },
    },

    {
      id: "device-2",
      type: "fraud",
      position: { x: 350, y: 420 },
      data: {
        type: "Device",
        value: "DEV-318",
      },
    },

    {
      id: "ip-1",
      type: "fraud",
      position: { x: 660, y: 180 },
      data: {
        type: "IP Address",
        value: "192.168.1.24",
      },
    },

    {
      id: "ip-2",
      type: "fraud",
      position: { x: 660, y: 420 },
      data: {
        type: "IP Address",
        value: "10.24.18.91",
      },
    },

    {
      id: "transaction-1",
      type: "fraud",
      position: { x: 970, y: 180 },
      data: {
        type: "Transaction",
        value: "TXN-78291",
        risk: 87,
      },
    },

    {
      id: "transaction-2",
      type: "fraud",
      position: { x: 970, y: 420 },
      data: {
        type: "Transaction",
        value: "TXN-78344",
        risk: 76,
      },
    },

    {
      id: "location-1",
      type: "fraud",
      position: { x: 1280, y: 180 },
      data: {
        type: "Location",
        value: "Islamabad",
      },
    },

    {
      id: "location-2",
      type: "fraud",
      position: { x: 1280, y: 420 },
      data: {
        type: "Location",
        value: "Rawalpindi",
      },
    },
  ],

  edges: [
    {
      id: "e1",
      source: "customer-1",
      target: "device-1",
      label: "USES",
    },

    {
      id: "e2",
      source: "customer-1",
      target: "ip-1",
      label: "CONNECTED FROM",
    },

    {
      id: "e3",
      source: "customer-2",
      target: "device-1",
      label: "USES",
    },

    {
      id: "e4",
      source: "customer-2",
      target: "ip-1",
      label: "CONNECTED FROM",
    },

    {
      id: "e5",
      source: "customer-3",
      target: "device-2",
      label: "USES",
    },

    {
      id: "e6",
      source: "customer-3",
      target: "ip-2",
      label: "CONNECTED FROM",
    },

    {
      id: "e7",
      source: "device-1",
      target: "transaction-1",
      label: "USED FOR",
    },

    {
      id: "e8",
      source: "ip-1",
      target: "transaction-1",
      label: "ORIGIN",
    },

    {
      id: "e9",
      source: "device-2",
      target: "transaction-2",
      label: "USED FOR",
    },

    {
      id: "e10",
      source: "ip-2",
      target: "transaction-2",
      label: "ORIGIN",
    },

    {
      id: "e11",
      source: "transaction-1",
      target: "location-1",
      label: "OCCURRED IN",
    },

    {
      id: "e12",
      source: "transaction-2",
      target: "location-2",
      label: "OCCURRED IN",
    },
  ],
};