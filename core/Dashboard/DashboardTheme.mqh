//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DashboardTheme.mqh                                     |
//| Layer   : Core / Dashboard                                       |
//| Version : 1.0.0                                                  |
//| Purpose : Dashboard Theme                                        |
//+------------------------------------------------------------------+

#ifndef CORE_DASHBOARD_DASHBOARDTHEME_MQH
#define CORE_DASHBOARD_DASHBOARDTHEME_MQH

class CDashboardTheme
{
private:

   color m_backgroundColor;
   color m_panelColor;
   color m_textColor;
   color m_successColor;
   color m_warningColor;
   color m_errorColor;

public:

   //--------------------------------------------------

   CDashboardTheme()
   {
      LoadDefault();
   }

   //--------------------------------------------------

   void LoadDefault()
   {
      m_backgroundColor = clrBlack;
      m_panelColor      = clrDarkSlateGray;
      m_textColor       = clrWhite;
      m_successColor    = clrLime;
      m_warningColor    = clrYellow;
      m_errorColor      = clrRed;
   }

   //--------------------------------------------------

   color BackgroundColor() const
   {
      return m_backgroundColor;
   }

   //--------------------------------------------------

   color PanelColor() const
   {
      return m_panelColor;
   }

   //--------------------------------------------------

   color TextColor() const
   {
      return m_textColor;
   }

   //--------------------------------------------------

   color SuccessColor() const
   {
      return m_successColor;
   }

   //--------------------------------------------------

   color WarningColor() const
   {
      return m_warningColor;
   }

   //--------------------------------------------------

   color ErrorColor() const
   {
      return m_errorColor;
   }

};

#endif