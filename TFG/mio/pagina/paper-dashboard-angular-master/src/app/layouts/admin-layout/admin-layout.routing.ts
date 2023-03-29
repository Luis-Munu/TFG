import { Routes } from '@angular/router';
import { SearchComponent } from '../../pages/search/search.component';
import { ZonesComponent } from '../../pages/zones/zones.component';
import { UserComponent } from '../../pages/user/user.component';
import { TypographyComponent } from '../../pages/typography/typography.component';
import { IconsComponent } from '../../pages/icons/icons.component';
import { MapsComponent } from '../../pages/maps/maps.component';
import { NotificationsComponent } from '../../pages/notifications/notifications.component';
import { UpgradeComponent } from '../../pages/upgrade/upgrade.component';

export const AdminLayoutRoutes: Routes = [
    { path: 'search',         component: SearchComponent},
    { path: 'zones',          component: ZonesComponent },
    { path: 'user',           component: UserComponent },
    { path: 'typography',     component: TypographyComponent },
    { path: 'icons',          component: IconsComponent },
    { path: 'maps',           component: MapsComponent },
    { path: 'notifications',  component: NotificationsComponent },
    { path: 'upgrade',        component: UpgradeComponent }
];
