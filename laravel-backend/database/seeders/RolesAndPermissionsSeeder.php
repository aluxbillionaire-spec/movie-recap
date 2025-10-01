<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Role;
use Spatie\Permission\Models\Permission;

class RolesAndPermissionsSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Reset cached roles and permissions
        app()[\Spatie\Permission\PermissionRegistrar::class]->forgetCachedPermissions();

        // Create permissions
        $permissions = [
            'view projects',
            'create projects',
            'edit projects',
            'delete projects',
            'upload files',
            'view jobs',
            'manage jobs',
            'view analytics',
            'manage users',
            'manage roles',
        ];

        foreach ($permissions as $permission) {
            Permission::create(['name' => $permission]);
        }

        // Create roles and assign permissions
        $adminRole = Role::create(['name' => 'admin']);
        $adminRole->givePermissionTo(Permission::all());

        $userRole = Role::create(['name' => 'user']);
        $userRole->givePermissionTo([
            'view projects',
            'create projects',
            'edit projects',
            'upload files',
            'view jobs',
        ]);

        $guestRole = Role::create(['name' => 'guest']);
        $guestRole->givePermissionTo([
            'view projects',
        ]);
    }
}
