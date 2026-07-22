//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DashboardLayout.mqh                                    |
//| Layer   : Core / Dashboard                                       |
//| Version : 1.0.0                                                  |
//| Purpose : Dashboard Layout Manager                               |
//+------------------------------------------------------------------+

#ifndef CORE_DASHBOARD_DASHBOARDLAYOUT_MQH
#define CORE_DASHBOARD_DASHBOARDLAYOUT_MQH

class CDashboardLayout
{
private:
    int m_left;
    int m_top;
    int m_width;
    int m_height;

public:
    //--------------------------------------------------

    CDashboardLayout()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        m_left = 10;
        m_top = 20;
        m_width = 420;
        m_height = 300;
    }

    //--------------------------------------------------

    void SetPosition(
        const int left,
        const int top)
    {
        m_left = left;
        m_top = top;
    }

    //--------------------------------------------------

    void SetSize(
        const int width,
        const int height)
    {
        m_width = width;
        m_height = height;
    }

    //--------------------------------------------------

    int Left() const
    {
        return m_left;
    }

    //--------------------------------------------------

    int Top() const
    {
        return m_top;
    }

    //--------------------------------------------------

    int Width() const
    {
        return m_width;
    }

    //--------------------------------------------------

    int Height() const
    {
        return m_height;
    }

    //--------------------------------------------------

    bool IsValid() const
    {
        return (m_width > 0 && m_height > 0);
    }
};

#endif