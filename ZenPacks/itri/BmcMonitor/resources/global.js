Ext.onReady(function() {
  var DEVICE_GRID_ID = 'device_grid';

  Ext.ComponentMgr.onAvailable(DEVICE_GRID_ID, function() {
    var grid = Ext.getCmp(DEVICE_GRID_ID);
    var store = grid.getStore();

    // Add 'power_status' field to the Zenoss.device.DeviceModel model
    Zenoss.device.DeviceModel.prototype.fields.add(new Ext.data.Field({name: 'power_status', type: 'boolean'}));

    // Create the power status column    
    var power_status_column = Ext.create('Ext.grid.column.Column', {
      id: 'power_status',
      width: 100,
      dataIndex: 'power_status',
      header: _t('Power Status'),
      renderer: Zenoss.render.pingStatus
    });

    // Obtain the Power Status for each record in the store and assign it to the model
    store.each(function(record){
      Zenoss.remote.DeviceRouter.getInfo({uid: record.data.uid}, function(result){
        record.data.power_status = result.data.power_status;
        grid.getView().refresh();
      });
    });

    // Insert the power status column into the device grid
    grid.headerCt.insert(2, power_status_column);
    
    grid.getView().refresh();

  });
});

