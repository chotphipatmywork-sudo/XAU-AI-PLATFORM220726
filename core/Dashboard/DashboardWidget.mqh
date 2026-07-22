//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DashboardWidget.mqh                                    |
//| Layer   : Core / Dashboard                                       |
//| Version : 1.0.0                                                  |
//| Purpose : Dashboard Widget                                       |
//+------------------------------------------------------------------+

#ifndef CORE_DASHBOARD_DASHBOARDWIDGET_MQH
#define CORE_DASHBOARD_DASHBOARDWIDGET_MQH

class CDashboardWidget
{
private:
    string m_name;

    bool m_visible;

public:
    //--------------------------------------------------

    CDashboardWidget()
    {
        m_name = "";
        m_visible = true;
    }

    //--------------------------------------------------

    void SetName(const string name)
    {
        m_name = name;
    }

    //--------------------------------------------------

    string Name() const
    {
        return m_name;
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

    //--------------------------------------------------

    void Draw()
    {
        if (!m_visible)
            return;

        // Reserved for future
        // Draw Widget Content
    }

    //--------------------------------------------------

    void Reset()
    {
        m_name = "";
        m_visible = true;
    }
};

#endif