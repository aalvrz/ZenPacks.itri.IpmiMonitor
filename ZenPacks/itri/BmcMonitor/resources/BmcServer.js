Ext.onReady(function() {
  var DEVICE_DETAIL_BAR_ID = 'devdetailbar';

  Ext.ComponentMgr.onAvailable(DEVICE_DETAIL_BAR_ID, function() {
    var detailBar = Ext.getCmp(DEVICE_DETAIL_BAR_ID);

    // First, we create the new Power Status item
    var powerStatusItem = Zenoss.DeviceDetailItem.create({
        ref: 'pstatusitem',
        width: 98,
        label: _t('Power Status'),
        id: 'pstatusitem'
    });

    detailBar.addDeviceDetailBarItem(powerStatusItem, function(bar, data) {
        detailBar.pstatusitem.setText(Zenoss.render.pingStatusLarge(data.power_status));
    },
    ['power_status']);

  });
});


