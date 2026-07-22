//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DashboardManager.mqh                                   |
//| Layer   : Dashboard                                               |
//| Version : 1.0.0                                                  |
//| Purpose : Central Dashboard Manager                              |
//+------------------------------------------------------------------+

#ifndef CORE_DASHBOARD_DASHBOARDMANAGER_MQH
#define CORE_DASHBOARD_DASHBOARDMANAGER_MQH

class CDashboardManager
{
private:

   bool m_visible;

public:

   //--------------------------------------------------

   CDashboardManager()
   {
      m_visible = true;
   }

   //--------------------------------------------------

   bool Initialize()
   {
      return true;
   }

   //--------------------------------------------------

   void Update()
   {
      if(!m_visible)
         return;

      // Reserved for future
      // - AI Status
      // - Trend
      // - Risk
      // - Position
      // - Portfolio
      // - Money
      // - Performance
   }

   //--------------------------------------------------

   void Shutdown()
   {
   }

   //--------------------------------------------------

   void Show()
   {
      m_visible = true;
   }

   //--------------------------------------------------

   void Hide()
   {
      m_visible = false;
   }

   //--------------------------------------------------

   bool IsVisible() const
   {
      return m_visible;
   }

};

#endif